# src/tools/cost_research.py
from langchain_core.tools import tool
from tavily import TavilyClient
from config import TAVILY_API_KEY

tavily = TavilyClient(api_key=TAVILY_API_KEY)

@tool
def research_costs(query: str) -> str:
    """Research current real prices for travel expenses (hotels, tickets, food, transport) for a family of 4 in 2025-2026."""
    search_query = f"{query} family of 4 current prices 2025 OR 2026 Singapore site:tripadvisor.com OR site:booking.com OR site:kayak.com OR site:agoda.com"
    try:
        response = tavily.search(query=search_query, max_results=10)
        results = []
        for r in response.get("results", []):
            title = r.get("title", "No title")
            content = r.get("content", "")[:400]
            url = r.get("url", "")
            results.append(f"{title}\n{content}\nSource: {url}")
        return "\n\n".join(results) if results else "No reliable cost data found. Try more specific query."
    except Exception as e:
        return f"Cost research error: {str(e)}"