import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_TOKEN = os.getenv("TRAVELPAYOUTS_API_TOKEN")

def get_flights(origin, destination, date=None):
    url = "https://api.travelpayouts.com/v1/prices/cheap"

    params = {
        "origin": origin,
        "destination": destination,
        "token": "YOUR_API_KEY"
    }
    

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        flights = []

        for key, value in data.get("data", {}).items():
            flights.append({
                "airline": value.get("airline", "Unknown"),
                "price": value.get("price", "N/A")
            })

        return flights[:5]
  
    except Exception:
        print("Invalid flight API response:", response.text)
    return []
