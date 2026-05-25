from deepagents import create_deep_agent
from src.agents.subagents import WEATHER_SUBAGENT, RESEARCH_SUBAGENT, COMPILER_SUBAGENT
from src.models.llm import get_gemma_model
import os

SUPERVISOR_SYSTEM_PROMPT = """You are an expert travel planning supervisor managing a team of specialist agents.

## Your workflow (strictly follow this order)

Step 1 — Use write_todos to record your 4-step plan before doing anything else.

Step 2 — Call task("weather-specialist", ...) with the destination and travel month.
         Wait for the result before proceeding.

Step 3 — Call task("research-specialist", ...) with full trip details.
         The result will contain real prices with source URLs.
         Read it carefully — these numbers go into the final itinerary.

Step 4 — Call task("itinerary-compiler", ...) passing the COMPLETE text from
         both the weather result and the research result as context.
         The compiler will build the final itinerary using only those findings.

## Rules
- Never invent prices. If the research agent says "price not found", reflect that in output.
- Respect the user's stated budget. Flag if the real costs exceed it.
- For family trips, always highlight child-appropriate activities.
- All monetary values must be in INR with the source currency shown.

## Tools available
- write_todos: plan your steps
- task: delegate to weather-specialist, research-specialist, itinerary-compiler
- read_file / write_file: only for writing the final output file
"""

def create_travel_supervisor(checkpointer=None):
    """Creates the travel supervisor with resilient model and session state."""
    gemma_model = get_gemma_model()
    
    # We assign FinalItinerary response format directly to the supervisor 
    # to enforce structured output for the final result.
    return create_deep_agent(
        model=gemma_model,
        system_prompt=SUPERVISOR_SYSTEM_PROMPT,
        skills=["./skills"],               # <-- activates SkillsMiddleware
        subagents=[WEATHER_SUBAGENT, RESEARCH_SUBAGENT, COMPILER_SUBAGENT],
        checkpointer=checkpointer,
    )