# src/agents/supervisor.py
from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from src.tools.external_tools import internet_search, get_weather_forecast, search_places
from src.tools.cost_research import research_costs
from config import GOOGLE_API_KEY, GOOGLE_MODEL
import re
import os
from datetime import datetime
from src.tools.file_tools import save_text_file, read_text_file, list_directory_files

# Lightweight extractor LLM
extractor_llm = ChatGoogleGenerativeAI(model=GOOGLE_MODEL, temperature=0.3, google_api_key=GOOGLE_API_KEY)

# Extraction prompt
extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an expert at extracting travel details from user messages.
Return ONLY a valid JSON object with these keys:
- destination
- month_year (e.g., "January 2026")
- adults (integer)
- children (integer)
- budget (integer)
- currency (e.g., "INR")
- preferences (list of strings)

Use null if missing.
"""),
    ("human", "{user_query}")
])

def extract_travel_details(user_query: str) -> dict:
    chain = extraction_prompt | extractor_llm
    try:
        response = chain.invoke({"user_query": user_query})
        content = response.content
        if isinstance(content, list):
            content = " ".join([str(item.get("text", "")) for item in content if isinstance(item, dict) and "text" in item])
        json_match = re.search(r'\{.*\}', str(content), re.DOTALL)
        if json_match:
            import json
            return json.loads(json_match.group(0))
    except Exception as e:
        print(f"Extraction failed: {e}")

    # Fallback
    return {
        "destination": "your destination",
        "month_year": "your travel period",
        "adults": 2,
        "children": 0,
        "budget": 100000,
        "currency": "INR",
        "preferences": ["general interests"]
    }


def create_travel_agent(user_query: str):
    details = extract_travel_details(user_query)

    dest = details.get("destination", "your destination")
    period = details.get("month_year") or "your travel period"
    adults = details.get("adults", 2)
    children = details.get("children", 0)
    budget = details.get("budget", 100000)
    currency = details.get("currency", "INR")
    prefs = ", ".join(details.get("preferences", [])) or "wonderful experiences"

    now = datetime.now()
    date_str = now.strftime("%d%m%Y %H%M")
    safe_dest = dest.replace('/', '_').replace('\\', '_')
    save_dir = f"data/{date_str}-{safe_dest}"
    os.makedirs(save_dir, exist_ok=True)

    subagents = [
        {
            "name": "weather-specialist",
            "description": "Handles weather forecasting",
            "system_prompt": f"Use get_weather_forecast and then MUST use the save_text_file tool to write your detailed summary to {save_dir}/weather.txt including temperature, rain, and family tips.",
            "tools": [get_weather_forecast, save_text_file],
        },
        {
            "name": "research-specialist",
            "description": "Researches attractions, food, and real costs",
            "system_prompt": f"""
You are a thorough researcher.
Use internet_search, search_places, and research_costs.
You MUST use the save_text_file tool to write detailed findings to:
- {save_dir}/attractions.txt (family-friendly activities)
- {save_dir}/food.txt (local cuisine, restaurants)
- {save_dir}/costs.txt (hotels, tickets, transport, meals — use research_costs for accuracy)
""",
            "tools": [internet_search, search_places, research_costs, save_text_file],
        },
        {
            "name": "itinerary-compiler",
            "description": "Compiles final itinerary",
            "system_prompt": f"""
Use the read_text_file tool to read all files: {save_dir}/weather.txt, {save_dir}/attractions.txt, {save_dir}/food.txt, {save_dir}/costs.txt
Create a beautiful, realistic day-by-day itinerary.
Include meals, activities, transport, daily costs, and family tips.
Stay within budget using real prices from costs.txt.
Use the save_text_file tool to save the final itinerary as {save_dir}/final_itinerary.txt
""",
            "tools": [read_text_file, save_text_file],
        }
    ]

    dynamic_system_prompt = f"""
You are a professional Family Travel Planner.

Trip Details:
- Destination: {dest}
- Period: {period}
- Group: {adults} adults, {children} children
- Budget: {currency} {budget}
- Preferences: {prefs}

STRICT WORKFLOW — OBEY THIS:
1. FIRST: Call write_todos with exactly these 5 tasks:
   - Research weather in {dest} for {period} (save to {save_dir}/weather.txt)
   - Research top family-friendly attractions in {dest} (save to {save_dir}/attractions.txt)
   - Research local food and restaurants in {dest} (save to {save_dir}/food.txt)
   - Research real costs in {dest} using research_costs tool (save to {save_dir}/costs.txt)
   - Compile final day-by-day itinerary (save to {save_dir}/final_itinerary.txt)
2. Delegate each task using 'task' tool to correct subagent. The subagents MUST be instructed to use the save_text_file tool.
3. Wait for all research files to exist in {save_dir} (use list_directory_files tool).
4. Only then spawn itinerary-compiler.
5. NEVER guess prices — use research_costs results.
6. Keep total under {currency} {budget}.

Be patient and accurate.
"""

    # Main LLM with tools
    return create_deep_agent(
        model=f"google_genai:{GOOGLE_MODEL}",
        tools=[internet_search, get_weather_forecast, search_places, research_costs, save_text_file, read_text_file, list_directory_files],
        subagents=subagents,
        system_prompt=dynamic_system_prompt
    )