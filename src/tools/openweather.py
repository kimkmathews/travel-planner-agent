# src/tools/openweather.py
import requests
from langchain_core.tools import tool
from config import OPENWEATHERMAP_API_KEY

BASE_URL = "http://api.openweathermap.org/data/2.5/forecast"

@tool
def get_weather_forecast(location: str, days: int = 5) -> str:
    """
    Get weather forecast for a location (city name or 'Goa, India').
    Returns summary for next few days.
    """
    if not OPENWEATHERMAP_API_KEY:
        return "OpenWeatherMap API key not configured."
    
    params = {
        "q": location,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric",
        "cnt": days * 8  # 3-hour intervals
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        if response.status_code != 200:
            return f"Error: {response.status_code} - {response.text}"
        
        data = response.json()
        city = data["city"]["name"]
        forecasts = []
        
        for item in data["list"][::8]:  # Take one per day
            date = item["dt_txt"].split()[0]
            temp = item["main"]["temp"]
            desc = item["weather"][0]["description"]
            forecasts.append(f"{date}: {temp}°C, {desc.capitalize()}")
        
        result = f"Weather forecast for {city}:\n" + "\n".join(forecasts)
        return result
    
    except Exception as e:
        return f"Error fetching weather: {str(e)}"