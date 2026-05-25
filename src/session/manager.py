import uuid
from typing import Optional
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from src.agents.supervisor import create_travel_supervisor
from src.models.schemas import FinalItinerary
from src.agents.extractor import extract_trip_parameters
from src.session.store import get_checkpointer

class TravelPlannerSession:
    """
    Manages a single user's conversation session with the travel planner.

    Each session has a stable thread_id. Calling .chat() multiple times
    within the same session continues the same conversation — the agent
    retains all research from previous turns.
    """

    def __init__(self, thread_id: Optional[str] = None):
        self.thread_id = thread_id or f"travel-{uuid.uuid4().hex[:8]}"
        self.checkpointer = get_checkpointer()
        self.agent = create_travel_supervisor(checkpointer=self.checkpointer)
        self._config = {"configurable": {"thread_id": self.thread_id}}
        self._printed_message_ids = set()
        print(f"📋 Session started: {self.thread_id}")

    def _has_history(self) -> bool:
        """Check if this session already has conversation history."""
        # Checkpointer get_tuple will return a tuple if history exists
        return self.checkpointer.get_tuple(self._config) is not None

    def chat(self, user_message: str, stream: bool = True) -> dict:
        """
        Send a message and receive the agent's response.

        On the first message, the full research pipeline runs.
        On follow-up messages, the agent uses cached research and
        answers conversationally — much faster.

        Args:
            user_message: The user's natural language input.
            stream: If True, prints output progressively; if False, returns silently.

        Returns:
            dict with keys: 'text_response', 'structured_itinerary' (if produced),
                            'thread_id', 'warnings'
        """
        if not self._has_history():
            from datetime import datetime
            ts = datetime.now().strftime("[%H:%M:%S]")
            print(f"\n{ts} ⏳ Extracting trip parameters from your query...")
            try:
                params = extract_trip_parameters(user_message)
                print(f"{ts} ✅ Parameter extraction complete.")
                # Prepend structured context to the message for the supervisor
                enriched_message = (
                    f"{user_message}\n\n"
                    f"[PARSED TRIP PARAMETERS]\n"
                    f"Origin: {params.origin_city}\n"
                    f"Destination: {params.destination}\n"
                    f"Duration: {params.duration_days} days\n"
                    f"Party: {params.num_adults} adults, {params.num_children} children\n"
                    f"Budget: ₹{params.budget_inr:,}\n"
                    f"Month: {params.travel_month}\n"
                    f"Preferences: {', '.join(params.preferences)}\n"
                )
            except Exception as e:
                print(f"⚠️ Parameter extraction failed ({e}), proceeding with raw query")
                enriched_message = user_message
        else:
            enriched_message = user_message  # Follow-up: use as-is

        inputs = {"messages": [HumanMessage(content=enriched_message)]}
        result_state = {}
        warnings = []

        if stream:
            for chunk in self.agent.stream(
                inputs,
                config=self._config,
                stream_mode="values"
            ):
                result_state = chunk
                self._print_chunk(chunk)
        else:
            result_state = self.agent.invoke(inputs, config=self._config)

        # Extract structured output if present
        structured: Optional[FinalItinerary] = result_state.get("structured_response")
        if structured and isinstance(structured, FinalItinerary):
            warnings = self._check_for_unverified_costs(structured)

        # Extract final text message
        messages = result_state.get("messages", [])
        text_response = ""
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content:
                text_response = (
                    msg.content if isinstance(msg.content, str)
                    else " ".join(
                        b.get("text", "") for b in msg.content
                        if isinstance(b, dict)
                    )
                )
                break

        return {
            "thread_id": self.thread_id,
            "text_response": text_response,
            "structured_itinerary": structured,
            "warnings": warnings,
        }

    def _check_for_unverified_costs(self, itinerary: FinalItinerary) -> list[str]:
        """Return warning strings for any unverified cost line items."""
        warnings = []
        for item in itinerary.cost_breakdown.line_items:
            if not item.is_verified or not item.source_url:
                warnings.append(
                    f"⚠️  Unverified cost: {item.description} — "
                    f"₹{item.amount_inr:,} (no source URL)"
                )
        if itinerary.cost_breakdown.unverified_items:
            for u in itinerary.cost_breakdown.unverified_items:
                warnings.append(f"⚠️  Price not found during research: {u}")
        return warnings

    def _print_chunk(self, chunk: dict):
        """Pretty-print streaming chunks to console."""
        from datetime import datetime
        
        messages = chunk.get("messages", [])
        if not messages:
            return
            
        for msg in messages:
            msg_id = getattr(msg, "id", None) or id(msg)
            if msg_id in self._printed_message_ids:
                continue
            self._printed_message_ids.add(msg_id)
            
            ts = datetime.now().strftime("[%H:%M:%S]")

            if isinstance(msg, AIMessage):
                content = msg.content
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict):
                            if block.get("type") == "thinking":
                                print(f"\n{ts} 🧠 [Thinking]: {block.get('thinking', '')[:200]}...")
                            elif block.get("type") == "text" and block.get("text"):
                                print(f"\n{ts} 🤖 [Agent Output]:\n{block['text']}")
                elif content:
                    print(f"\n{ts} 🤖 [Agent Output]:\n{content}")
                    
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        name = tc.get("name", "?")
                        args = tc.get("args", {})
                        print(f"\n{ts} 🛠️  [Tool Call]: {name}\n   Inputs: {args}")
                print("-" * 60)

            elif getattr(msg, "type", "") == "tool" or msg.__class__.__name__ == "ToolMessage":
                content_str = str(msg.content)
                if len(content_str) > 1000:
                    content_str = content_str[:1000] + "\n... [Output Truncated for readability]"
                name = getattr(msg, "name", "Unknown")
                print(f"\n{ts} ✅ [Tool Output] (from '{name}'):\n{content_str}")
                print("-" * 60)

    @classmethod
    def restore(cls, thread_id: str) -> "TravelPlannerSession":
        """
        Restore an existing session by thread_id.
        The conversation history is loaded from the checkpointer.
        """
        session = cls(thread_id=thread_id)
        print(f"🔄 Restored session: {thread_id}")
        return session
