# src/tools/osm_places.py (updated version)
from langchain_core.tools import tool
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time

# Initialize with a unique user agent (required by OSM policy)
geolocator = Nominatim(user_agent="travel-itinerary-planner/1.0", timeout=10)

@tool
def osm_places_search(query: str, max_results: int = 5) -> str:
    """
    Search for points of interest, attractions, restaurants, hotels, etc. using OpenStreetMap's Nominatim.
    
    Args:
        query: The search query, e.g., 'beaches in Goa', 'restaurants in Calangute'
        max_results: Maximum number of results to return (default 5)
    
    Returns:
        A string with formatted results including name, address, coordinates, and type.
    """
    # Improve query for better results
    if "goa" in query.lower() and "india" not in query.lower():
        query = f"{query}, India"
    
    try:
        time.sleep(1.5)  # Polite delay to avoid rate limits

        locations = geolocator.geocode(query, exactly_one=False, limit=max_results)
        
        if not locations:
            # Try a fallback query variation
            fallback_query = query.replace("in Goa", "Goa").replace("beaches", "beach")
            locations = geolocator.geocode(fallback_query, exactly_one=False, limit=max_results)
        
        if not locations:
            return (
                f"No results found for '{query}'.\n\n"
                "Tips for better results:\n"
                "- Use specific locations: 'Palolem Beach Goa', 'restaurants Calangute'\n"
                "- Add 'India' if searching for Goa: 'beaches in Goa India'\n"
                "- Try nearby cities: 'hotels in Panaji Goa'"
            )
        
        results = []
        for loc in locations:
            result = (
                f"Name: {loc.address}\n"
                f"Type: {loc.raw.get('type', 'Unknown')}\n"
                f"Latitude: {loc.latitude}\n"
                f"Longitude: {loc.longitude}\n"
                f"Full Address: {loc.address}\n"
                "---"
            )
            results.append(result)
        
        return "\n".join(results)
    
    except GeocoderTimedOut:
        return "Timeout: The geocoding service took too long. Try again later."
    except GeocoderUnavailable:
        return "Service unavailable: Nominatim server is down or unreachable."
    except Exception as e:
        return f"Error during search: {str(e)}"