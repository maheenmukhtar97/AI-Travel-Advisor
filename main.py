from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from serpapi import GoogleSearch

from backend.agent import run_agent_async
from prompts.prompts import ITINERARY_PROMPT

from tools.flight_tools import get_flights
from tools.bus_tools import get_buses
from tools.train_tools import get_trains
from tools.hotel_tools import get_hotels
from tools.weather_tools import get_weather
from tools.attraction_tools import get_attractions
from tools.routes_tools import get_route
import asyncio

# ✅ Groq
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI(title="AI Travel Advisor Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # production mein Streamlit URL daal sakte ho
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------------- CITY NORMALIZATION ----------------
CITY_TO_IATA = {
    "lahore": "LHE",
    "karachi": "KHI",
    "islamabad": "ISB",
    "peshawar": "PEW",
    "quetta": "UET"
}

def normalize_city(city: str):
    city = city.lower().strip()

    # Match partial input (e.g. "Lahore Pakistan")
    for key in CITY_TO_IATA:
        if key in city:
            return CITY_TO_IATA[key]

    # If already IATA
    if len(city) == 3:
        return city.upper()

    return None

# ---------------- REQUEST MODEL ----------------
class TripRequest(BaseModel):
    source: str
    destination: str
    budget: int
    days: int
    trip_type: str
    flight_class: str
    hotel_rating: str
    budget_pref: str
    transport_modes: list[str]
    departure_date: str 
    

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # ✅ correct model
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant."},
                {"role": "user", "content": req.message}
            ],
            temperature=0.7
        )
        return {"response": response.choices[0].message.content}

    except Exception as e:
        return {"response": f"Error: {str(e)}"}

# ---------------- SAFE CALL WRAPPER ----------------
async def safe_call(func, *args):
    """
    Run any blocking function safely in a thread.
    If it fails, log the error and return empty list.
    """
    try:
        return await asyncio.to_thread(func, *args)
    except Exception as e:
        print(f"{func.__name__} Error:", e)
        return []


# ---------------- PLAN TRIP ----------------
@app.post("/plan-trip")
async def plan_trip(data: TripRequest):
    source_code = normalize_city(data.source)
    destination_code = normalize_city(data.destination)

    if not source_code or not destination_code:
        return {"error": "Invalid source or destination city"}

    source = data.source
    destination = data.destination
    budget = data.budget
    days = data.days
    trip_type = data.trip_type

    # 2️⃣ Run API calls concurrently
    from datetime import datetime, timedelta

    # Generate realistic dates
    today = datetime.today()
    travel_date = data.departure_date 
    checkin = (today + timedelta(days=10)).strftime("%Y-%m-%d")
    checkout = (today + timedelta(days=10 + data.days)).strftime("%Y-%m-%d")
    # Step 1: Call everything EXCEPT flights
    hotels, weather, attractions, route_task = await asyncio.gather(
        safe_call(get_hotels, destination, checkin, checkout),
        safe_call(get_weather, destination),
        safe_call(get_attractions, destination),
        safe_call(get_route, source, destination)
    )
    
    # 3️⃣ Smart filtering
    def clean_price(p):
        try:
            return int(str(p).replace(",", ""))
        except:
            return 999999
    
 
    flights = await safe_call(
        get_flights,
        source_code,
        destination_code,
        travel_date,
        data.flight_class
        )

    flights = sorted(flights, key=lambda x: clean_price(x.get("price"))) if flights else []
    flights = flights[:5]
    # Step 4: Final fallback (your existing dummy)
    if not flights or len(flights) == 0:
        print("⚠️ No flights from API, using fallback")
        if destination.lower() == "karachi":
            flights = [
                {
                    "airline": "PIA",
                    "departure": "09:00 AM",
                    "arrival": "10:30 AM",
                    "duration": "1h 30m",
                    "price": 25000,
                    "note": "Estimated fare"
                },
                {
                    "airline": "AirBlue",
                    "departure": "01:00 PM",
                    "arrival": "02:20 PM",
                    "duration": "1h 20m",
                    "price": 22000,
                    "note": "Estimated fare"
                },
                {
                    "airline": "SereneAir",
                    "departure": "06:00 PM",
                    "arrival": "07:25 PM",
                    "duration": "1h 25m",
                    "price": 24000,
                    "note": "Estimated fare"
                }
            ]

        elif destination.lower() == "lahore":
            flights = [
                {
                    "airline": "PIA",
                    "departure": "08:00 AM",
                    "arrival": "09:15 AM",
                    "duration": "1h 15m",
                    "price": 23000,
                    "note": "Estimated fare"
                },
                {
                    "airline": "AirBlue",
                    "departure": "12:00 PM",
                    "arrival": "01:20 PM",
                    "duration": "1h 20m",
                    "price": 21000,
                    "note": "Estimated fare"
                },
                {
                    "airline": "SereneAir",
                    "departure": "06:00 PM",
                    "arrival": "07:25 PM",
                    "duration": "1h 25m",
                    "price": 24000,
                    "note": "Estimated fare"
                }
            ]

        else:
        # 🌍 Generic fallback
            flights = [
                {
                    "airline": "Local Airline",
                    "departure": "10:00 AM",
                    "arrival": "12:00 PM",
                    "duration": "2h",
                    "price": 20000,
                    "note": "Estimated fare"
                 }
                ]
    print("Flights API Response:", flights)
    print("Hotels API Response:", hotels)
    print("Weather API Response:", weather)

    # 🚌🚆 Transport options
    buses = []
    trains = []

    if any("bus" in mode.lower() for mode in data.transport_modes):
        buses = await safe_call(get_buses, source, destination)

    if any("train" in mode.lower() for mode in data.transport_modes):
        trains = await safe_call(get_trains, source, destination)

    buses = sorted(buses, key=lambda x: x["price"]) if buses else []
    trains = sorted(trains, key=lambda x: x["price"]) if trains else []

    hotels = hotels[:5] if hotels else []
    
    if not hotels:
        if destination.lower() == "karachi":
            hotels = [
                {"name": "Pearl Continental Hotel Karachi", "price": 3000}, 
                {"name": "Hotel Excelsior Karachi saddar", "price": 15000}, 
                {"name": "Hotel Crown Inn Karachi", "price": 7000} 
            ]
        elif destination.lower() == "lahore":
            hotels = [
                {"name": "Hotel One Lahore", "price": 8000},
                {"name": "Pearl Continental Lahore", "price": 20000},
                {"name": "Avari Lahore", "price": 15000}
            ]
    else:
        hotels = hotels[:5]
    attractions = attractions[:5] if attractions else []

    # 4️⃣ Convert to text
    flights_text = (
        "\n".join([f"{f.get('airline','N/A')} | {f.get('price','N/A')} PKR" for f in flights])
        if flights else
        "No flights found from API. Do NOT assume flights exist."
     )
    hotels_text = "\n".join([f"{h.get('name','N/A')} | {h.get('price','N/A')} PKR" for h in hotels]) 
    attractions_text = "\n".join([f"{a.get('name','N/A')}" for a in attractions]) or "No attractions available"
    if isinstance(weather, list):
        weather_text = "\n".join([
            f"{day['date']}: 🌡️ {day['temp_day']}°C / {day['temp_night']}°C | {day['desc']}"
            for day in weather
        ])
    elif isinstance(weather, dict):
        weather_text = weather.get("error", "Weather unavailable")

    else:
        weather_text = "Weather unavailable"


    if data.budget_pref == "Luxury":
        budget_note = "User prefers luxury experiences. Avoid budget options."
    elif data.budget_pref == "Standard":
        budget_note = "Balance comfort and cost."
    else:
        budget_note = "Focus on cheapest options."

    trip_note = f"User is traveling from {source} to {destination}. Focus only on destination."
        
    # 5️⃣ Strong prompt
    prompt = f"""
You are an expert AI travel planner.

Create a detailed {days}-day travel plan where:

- The user STARTS from {source}
- Travels to {destination} on Day 1 (or before itinerary begins)
- The trip should be focused ONLY on {destination}

Trip Type:
- This is NOT a multi-city trip
- This is a destination-based trip

Important Rules:
- DO NOT create multiple days in {source}
- DO NOT treat {source} as a tourist destination
- All itinerary days should be in {destination}
- Travel from {source} → {destination} should happen at the beginning

Travel Direction:
From {source} to {destination}

Important:
- Lahore ↔ Karachi is a long-distance route
- Flights are fastest
- Buses and trains take significantly longer
- Suggest accordingly

Constraints:
- Budget: {budget} PKR (STRICT)
- Trip type: {trip_type}
- Budget Preference: {data.budget_pref}
- Flight Class: {data.flight_class}
- Hotel Rating: {data.hotel_rating}

User Intent:
{budget_note}

IMPORTANT:
- If budget_pref is Luxury → NEVER suggest cheap or budget options
- Use words like premium, luxury, high-end

{trip_note}

Available Transport Modes:
{data.transport_modes}

Instructions:
- Suggest ONLY selected transport types
- Compare options if multiple selected
- If flights + bus → suggest best one based on budget & comfort

Rules:
- If Luxury → suggest premium experiences, not cheapest
- If Business/First Class → prioritize comfort over price
- If 5 Star → suggest high-end hotels only
- Avoid budget/cheap suggestions unless explicitly Economy

Use this data:
Route Information:
Distance: {route_task.get('distance', 'N/A')}
Flight Time: {route_task.get('flight_time', 'N/A')}
Train Time: {route_task.get('train_time', 'N/A')}
Bus Time: {route_task.get('bus_time', 'N/A')}


Flights:
{flights_text}
Note:
If flights contain "Estimated fare", mention they are approximate.

Hotels:
{hotels_text}

Weather:
{weather_text}

Attractions:
{attractions_text}


Instructions:
- Choose the BEST options within budget
- If budget_pref is Luxury → prioritize premium options
- If Economy → prioritize cheapest options
- Provide day-wise plan (Day 1, Day 2...)
- Suggest food, transport, and tips
- If budget is low → suggest alternatives (bus/train)
- Be realistic and specific
"""

    # 6️⃣ Call Groq LLaMA 2–13B in thread
    def groq_call():
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # <-- LLaMA 2–13B
            messages=[
                {"role": "system", "content": "You are a smart travel planner AI."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content

    itinerary = await asyncio.to_thread(groq_call)

    # 7️⃣ Return final response
    return {
        "itinerary": itinerary,
        "flights": flights,
        "buses": buses,
        "trains": trains,
        "hotels": hotels,
        "weather": weather,
        "attractions": attractions,
        "route": route_task,
        "normalized": {
            "source": source_code,
            "destination": destination_code
        }
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)