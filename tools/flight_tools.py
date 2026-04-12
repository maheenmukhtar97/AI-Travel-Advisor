from serpapi import GoogleSearch
from dotenv import load_dotenv
import os

load_dotenv()

SERP_API_KEY = os.getenv("SERPAPI_API_KEY")

def get_flights(origin, destination, date=None, travel_class="Economy"):
    """
    Fetch flights using SerpAPI (Google Flights)
    """

    try:
        # ✅ DEBUG
        print("🧪 Incoming flight_class:", travel_class)

        # ✅ SAFE NORMALIZATION
        CLASS_MAP = {
            "economy": "1",
            "economy class": "1",
            "business": "3",
            "business class": "3",
            "first": "4",
            "first class": "4"
}

        if isinstance(travel_class, str):
            travel_class_clean = travel_class.strip().lower()
            travel_class = CLASS_MAP.get(travel_class_clean, "1")
        else:
            travel_class = "ECONOMY"

        print("✅ Mapped travel_class:", travel_class)

        # ✅ PARAMS
        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": date,
            "currency": "PKR",
            "hl": "en",
            "adults": 1,
            "travel_class": travel_class,
            "type": 2,   # one-way
            "api_key": SERP_API_KEY
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        print("🔍 RAW FLIGHT API RESPONSE:", results)
        if not results.get("best_flights") and not results.get("other_flights"):
            print("⚠️ No flights found → retrying with Economy")

        params["travel_class"] = "1"  # Economy
        search = GoogleSearch(params)
        results = search.get_dict()   

        flights = []

        if "best_flights" in results:
            for flight in results.get("best_flights", []):
                segments = flight.get("flights", [])
                if not segments:
                    continue

                segment = segments[0]

                try:
                    price = int(str(flight.get("price", 0)).replace(",", ""))
                except:
                    price = 999999
                if not price:
                    continue

                duration_mins = flight.get("total_duration", 0)
                try:
                    hours = duration_mins // 60
                    mins = duration_mins % 60
                    duration = f"{hours}h {mins}m"
                except:
                    duration = "N/A"

                flights.append({
                    "airline": segment.get("airline", "N/A"),
                    "departure": segment.get("departure_airport", {}).get("time", "N/A"),
                    "arrival": segment.get("arrival_airport", {}).get("time", "N/A"),
                    "duration": duration,
                    "price": f"{price:,}"
                })

        elif "other_flights" in results:
            for flight in results["other_flights"][:5]:
                segment = flight["flights"][0]

                flights.append({
                    "airline": segment.get("airline", "N/A"),
                    "departure": segment.get("departure_airport", {}).get("time", "N/A"),
                    "arrival": segment.get("arrival_airport", {}).get("time", "N/A"),
                    "duration":duration,
                    "price": f"{price:,}"
                })

        return flights[:5]
        
    except Exception as e:
        print("❌ SerpAPI Flight Error:", e)
        return []

    