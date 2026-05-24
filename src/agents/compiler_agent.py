# src/agents/compiler_agent.py
from deepagents import create_deep_agent

compiler_agent = create_deep_agent(
    name="CompilerAgent",
    system_prompt="""
You are the final compiler. Read all research files:
- todos.txt
- weather.txt
- attractions.txt
- food.txt

Then create a beautiful, detailed day-by-day itinerary for the family trip.
Include:
- Daily activities
- Meal suggestions
- Estimated daily costs
- Tips for traveling with kids

Save the final itinerary as final_itinerary.txt
"""
)