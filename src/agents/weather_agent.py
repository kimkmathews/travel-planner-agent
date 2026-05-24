# src/agents/weather_agent.py
from deepagents import create_deep_agent
from src.tools.external_tools import get_weather

weather_agent = create_deep_agent(
    name="WeatherAgent",
    system_prompt="""
You are a weather specialist. Fetch and summarize the weather forecast.
Write a clear summary to weather.txt
""",
    tools=[get_weather]
)