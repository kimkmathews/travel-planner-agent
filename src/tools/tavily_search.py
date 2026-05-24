# src/tools/tavily_search.py
from tavily import TavilyClient
from langchain_core.tools import tool
from config import TAVILY_API_KEY

@tool
def tavily_search(query: str) -> str:
    """Search the web using Tavily for travel information, events, tips, etc."""
    client = TavilyClient(api_key=TAVILY_API_KEY)
    try:
        response = client.search(query, max_results=5)
        return str(response)
    except Exception as e:
        return f"Error with Tavily search: {str(e)}"