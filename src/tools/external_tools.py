# src/tools/external_tools.py
from langchain_core.tools import tool
from tavily import TavilyClient
import requests
from config import TAVILY_API_KEY, OPENWEATHERMAP_API_KEY

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

@tool
def internet_search(query: str) -> str:
    """Search the web for travel information."""
    try:
        response = tavily_client.search(query, max_results=6)
        results = [f"{r['title']}: {r['content'][:300]}" for r in response.get("results", [])]
        return "\n\n".join(results) or "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"

@tool
def get_weather_forecast(location: str) -> str:
    """Get weather forecast for a location."""
    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {"q": location, "appid": OPENWEATHERMAP_API_KEY, "units": "metric"}
    try:
        r = requests.get(url, params=params).json()
        if r.get("cod") != "200":
            return f"Weather error: {r.get('message')}"
        summaries = []
        for item in r["list"][:8]:
            date = item["dt_txt"].split()[0]
            temp = item["main"]["temp"]
            desc = item["weather"][0]["description"]
            summaries.append(f"{date}: {temp}°C, {desc}")
        return f"Weather in {location}:\n" + "\n".join(summaries)
    except Exception as e:
        return f"Weather fetch failed: {str(e)}"

@tool
def search_places(query: str) -> str:
    """Search for places using Nominatim (OSM)."""
    from src.tools.osm_places import osm_places_search
    return osm_places_search.invoke(query)