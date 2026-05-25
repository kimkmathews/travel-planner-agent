from deepagents import create_deep_agent
from src.models.llm import get_fast_model
from src.models.schemas import TripParameters

EXTRACTOR_PROMPT = """You are a travel query parser.

Extract the structured travel parameters from the user's message.
If any field is not mentioned, make a reasonable assumption and note it.
For budget, if given in any currency convert to INR.
For party composition, infer from context (e.g. "family trip for 3" with no age info → 2 adults, 1 child)."""

def extract_trip_parameters(user_query: str) -> TripParameters:
    """
    Parse a natural language travel query into a structured TripParameters object.

    Uses a fast lightweight model — no tools needed, just extraction.
    """
    extractor = create_deep_agent(
        model=get_fast_model(),
        system_prompt=EXTRACTOR_PROMPT,
        response_format=TripParameters,
    )
    result = extractor.invoke({
        "messages": [{"role": "user", "content": user_query}]
    })
    params: TripParameters = result["structured_response"]
    return params
