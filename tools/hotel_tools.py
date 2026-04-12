from serpapi import GoogleSearch
from dotenv import load_dotenv
import os

load_dotenv()

SERP_API_KEY = os.getenv("SERPAPI_API_KEY")


def extract_price(place):
    try:
        if "price" in place:
            return place["price"]
        elif "price_level" in place:
            # Convert price_level (1–4) to PKR estimate
            return place["price_level"] * 5000
        else:
            return "N/A"
    except:
        return "N/A"


def get_hotels(city, checkin=None, checkout=None):
    """
    Fetch hotels using SerpAPI (Google Maps)
    """

    try:
        params = {
            "engine": "google_maps",
            "q": f"hotels in {city}",
            "type": "search",
            "api_key": SERP_API_KEY
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        hotels = []

        for place in results.get("local_results", [])[:5]:
            raw_price = place.get("price", "")

            try:
                raw_price = str(raw_price).split("-")[0]
                usd_price = int(raw_price.replace("$", "").strip())
                pkr_price = usd_price * 280
                price = f"{pkr_price:,} "
            except:
                price = "N/A"
            hotels.append({
                "name": place.get("title", "N/A"),
                "rating": place.get("rating", "N/A"),
                "reviews": place.get("reviews", "N/A"),
                "address": place.get("address", "N/A"),
                "currency": "PKR",
                "price": price,
                "type": place.get("type", "Hotel")
            })

        return hotels

    except Exception as e:
        print("❌ SerpAPI Hotel Error:", e)
        return []