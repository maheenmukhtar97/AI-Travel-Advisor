import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_TOKEN = os.getenv("TRAVELPAYOUTS_API_TOKEN")

import requests

def get_hotels(city, checkin=None, checkout=None):
    url = "https://engine.hotellook.com/api/v2/cache.json"

    params = {
        "location": city,
        "currency": "PKR",
        "limit": 5
    }

    try:
        res = requests.get(url, params=params, timeout=5)
        data = res.json()

        hotels = []

        for h in data[:5]:
            hotels.append({
                "name": h.get("hotelName", "Hotel"),
                "price": h.get("priceAvg", "N/A")
            })

        return hotels

    except Exception as e:
        print("Hotel API Error:", e)
        return []