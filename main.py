from fastapi import FastAPI
from pydantic import BaseModel

from backend.agent import run_agent_async
from prompts.prompts import ITINERARY_PROMPT

from tools.flight_tools import get_flights
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

# ---------------- ASYNC TOOLS ----------------
# Here we wrap the existing sync tools to async using asyncio.to_thread

from tools.flight_tools import get_flights
from tools.hotel_tools import get_hotels
from tools.weather_tools import get_weather
from tools.attraction_tools import get_attractions
from tools.routes_tools import get_route


async def async_get_flights(source, destination, date):
    return await asyncio.to_thread(get_flights, source, destination, date)

async def async_get_hotels(city, checkin, checkout):
    return await asyncio.to_thread(get_hotels, city, checkin, checkout)

async def async_get_attractions(city):
    return await asyncio.to_thread(get_attractions, city)

async def async_get_weather(city):
    # get_weather uses requests (blocking), so run in thread
    return await asyncio.to_thread(get_weather, city)

async def async_get_route(source, destination):
    from tools.routes_tools import get_route
    return await asyncio.to_thread(get_route, source, destination)

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
    travel_date = (today + timedelta(days=10)).strftime("%Y-%m-%d")
    checkin = (today + timedelta(days=10)).strftime("%Y-%m-%d")
    checkout = (today + timedelta(days=10 + data.days)).strftime("%Y-%m-%d")

    flights, hotels, weather, attractions, route_task = await asyncio.gather(
    safe_call(get_flights, source_code, destination_code, travel_date),
    safe_call(get_hotels, destination, checkin, checkout),
    safe_call(get_weather, destination),
    safe_call(get_attractions, destination),
    safe_call(get_route, source, destination)
)
    print("Flights API Response:", flights)
    print("Hotels API Response:", hotels)
    print("Weather API Response:", weather)

    # 3️⃣ Smart filtering
    def clean_price(p):
        try:
            return int(str(p).replace(",", ""))
        except:
            return 999999

    flights = sorted(
        flights,
        key=lambda x: clean_price(x.get("price"))
    )[:3]
    if not flights:
        flights = [
            {"airline": "PIA", "price": 25000, "note": "Estimated fare"},
            {"airline": "AirBlue", "price": 22000, "note": "Estimated fare"},
            {"airline": "SereneAir", "price": 24000, "note": "Estimated fare"}
        ]
    hotels = hotels[:5] if hotels else []
    
    if not hotels:
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
    hotels_text = "\n".join([f"{h.get('name','N/A')} | {h.get('price','N/A')} PKR" for h in hotels]) or "No hotels available"
    attractions_text = "\n".join([f"{a.get('name','N/A')}" for a in attractions]) or "No attractions available"
    if isinstance(weather, list):
        weather_text = "\n".join([
            f"{day['date']}: 🌡️ {day['temp_day']}°C / {day['temp_night']}°C | {day['desc']}"
            for day in weather
        ])
    else:
        weather_text = "Weather unavailable"
    
    # 5️⃣ Strong prompt
    prompt = f"""
You are an expert AI travel planner.

Create a detailed {days}-day itinerary from {source} to {destination}.

Constraints:
- Budget: {budget} PKR (STRICT)
- Trip type: {trip_type}

Use this data:
Route Information:
Distance: {route_task.get('distance_km', 'N/A')} km
Travel Time: {route_task.get('duration_hr', 'N/A')} hours

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
- Prioritize cheapest flights and hotels
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
        "hotels": hotels,
        "weather": weather,
        "attractions": attractions,
        "route": route_task,
        "normalized": {
            "source": source_code,
            "destination": destination_code
        }
    }