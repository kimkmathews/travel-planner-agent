# src/agents/research_agent.py
from deepagents import create_deep_agent
from src.tools.external_tools import web_search, places_search

research_agent = create_deep_agent(
    name="ResearchAgent",
    system_prompt="""
You are a travel researcher. Your job is to find:
- Top family-friendly beaches and attractions in the destination
- Best local food and restaurants
- Light adventure activities suitable for kids
Use web_search and places_search tools.
Write detailed findings to files: attractions.txt, food.txt
""",
    tools=[web_search, places_search]
)