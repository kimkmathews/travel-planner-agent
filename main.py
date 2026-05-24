# main.py
from dotenv import load_dotenv
load_dotenv()
import time  
import shutil
import os

# --- Rate limiting patch for Google GenAI ---
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
_original_generate = ChatGoogleGenerativeAI._generate
def _rate_limited_generate(*args, **kwargs):
    time.sleep(4.1) # Sleep to respect 15 requests/minute quota
    return _original_generate(*args, **kwargs)
ChatGoogleGenerativeAI._generate = _rate_limited_generate
# --------------------------------------------

# Clear workspace
if os.path.exists("data/temp"):
    shutil.rmtree("data/temp")
os.makedirs("data/temp", exist_ok=True)
os.makedirs("data/itineraries", exist_ok=True)

from src.agents.supervisor import create_travel_agent
from langchain_core.messages import HumanMessage

print("🧳 Deep Agents Travel Planner Starting...\n")

user_query = """Plan a 5-day family trip to Phu Quoc from Kochi in November 2026 for 2 adults and 1 kids.
Budget: ₹200,000. We love beaches, food, and light adventure."""

# Create agent with dynamic extraction
supervisor_agent = create_travel_agent(user_query)

inputs = {"messages": [HumanMessage(content=user_query)]}

print(f"User: {user_query}\n")
print("Agent thinking...\n")

from langchain_core.messages import AIMessage, ToolMessage

for chunk in supervisor_agent.stream(inputs, stream_mode="values"):
    messages = chunk.get("messages", [])
    if messages:
        last_msg = messages[-1]
        
        if isinstance(last_msg, AIMessage):
            # Handle string vs list content (Google GenAI can return lists with 'thinking' blocks)
            if isinstance(last_msg.content, list):
                for block in last_msg.content:
                    if isinstance(block, dict):
                        if block.get("type") == "thinking":
                            print(f"🧠 [Agent Thinking]:\n{block.get('thinking', '')}")
                        elif block.get("type") == "text":
                            print(f"🤖 [Agent Output]:\n{block.get('text', '')}")
            elif last_msg.content:
                print(f"🤖 [Agent Output]:\n{last_msg.content}")
            
            # Show tool calls
            if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                for tool_call in last_msg.tool_calls:
                    print(f"🛠️ [Calling Tool]: {tool_call.get('name', 'Unknown')}")
                    print(f"   Inputs: {tool_call.get('args', {})}")
            
            print("\n" + "-"*70 + "\n")
            
        elif isinstance(last_msg, ToolMessage):
            content_str = str(last_msg.content)
            if len(content_str) > 1000:
                content_str = content_str[:1000] + "\n... [Output Truncated for readability]"
            print(f"✅ [Tool Output] (from '{last_msg.name}'):\n{content_str}")
            print("\n" + "-"*70 + "\n")