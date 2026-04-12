from serpapi import GoogleSearch
from dotenv import load_dotenv
import os

load_dotenv()

SERP_API_KEY = os.getenv("SERPAPI_API_KEY")


def get_attractions(city):
    try:
        params = {
            "engine": "google_maps",
            "q": f"top tourist attractions in {city} Pakistan",
            "type": "search",
            "api_key": SERP_API_KEY
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        attractions = []

        for place in results.get("local_results", [])[:5]:
            attractions.append({
                "name": place.get("title", "N/A"),
                "rating": place.get("rating", "N/A"),
                "reviews": place.get("reviews", "N/A"),
                "address": place.get("address", "N/A"),
                "type": place.get("type", "Attraction")
            })

        if attractions:
            return attractions

    except Exception as e:
        print("❌ SerpAPI Attraction Error:", e)

    # 🔥 fallback (VERY IMPORTANT)
    if "karachi" in city.lower():
        return [
            {"name": "Clifton Beach"},
            {"name": "Quaid-e-Azam Mausoleum"},
            {"name": "Dolmen Mall Clifton"},
            {"name": "Port Grand"},
            {"name": "Frere Hall"}
        ]

    elif "lahore" in city.lower():
        return [
            {"name": "Badshahi Mosque"},
            {"name": "Lahore Fort"},
            {"name": "Minar-e-Pakistan"},
            {"name": "Shalimar Gardens"},
            {"name": "Wagah Border"}
        ]

    return [{"name": f"Popular attractions in {city}"}]