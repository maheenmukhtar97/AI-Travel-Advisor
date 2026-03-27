from serpapi import GoogleSearch
from dotenv import load_dotenv
import os

load_dotenv()

SERP_API_KEY = os.getenv("SERPAPI_API_KEY")

def get_attractions(city):

    params = {
        "engine": "google_maps",
        "q": f"tourist attractions in {city}",
        "api_key": SERP_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    places = []

    for p in results.get("local_results", [])[:5]:
        places.append({
            "name": p.get("title", "Unknown Place"),
            "rating": p.get("rating", "N/A")
        })

    # ✅ fallback if empty
    if not places:
        places = [
            {"name": "Badshahi Mosque"},
            {"name": "Lahore Fort"},
            {"name": "Minar-e-Pakistan"},
            {"name": "Shalimar Gardens"},
            {"name": "Wagah Border"}
        ]

    return places