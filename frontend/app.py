import streamlit as st
import requests
from datetime import date

import streamlit as st
import requests
from datetime import date

# ✅ ADD IT HERE (helper function section)
def normalize_flights(flights):
    normalized = []

    for f in flights:
        normalized.append({
            "airline": f.get("airline") or f.get("name"),
            "departure": f.get("departure") or f.get("departure_time"),
            "arrival": f.get("arrival") or f.get("arrival_time"),
            "duration": f.get("duration"),
            "price": f.get("price") or f.get("ticket_price")
        })

    return normalized

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AI Travel Planner ✈️",
    page_icon="🌍",
    layout="wide"
)
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
    color: black;
}

/* 🌸 Soft pastel violet background */
.main {
    background: linear-gradient(135deg, #f3e8ff, #e9d5ff, #fce7f3);
    color: black;
}

/* 🖤 Centered BLACK heading */
.main-title {
    text-align: center;
    font-size: 3rem;
    font-weight: 700;
    color: black;   /* 👈 important */
    margin-bottom: 10px;
}

/* Subtitle */
.subtitle {
    text-align: center;
    color: #444;
    margin-bottom: 30px;
}

/* 🔘 Soft pastel buttons */
.stButton>button {
    border-radius: 25px;
    background: #d8b4fe;
    color: black;
    padding: 10px 25px;
    border: none;
    transition: 0.3s;
}

.stButton>button:hover {
    background: #c084fc;
    transform: scale(1.05);
}

/* 🧊 Light cards */
.card {
    background: rgba(255, 255, 255, 0.7);
    padding: 15px;
    border-radius: 15px;
    backdrop-filter: blur(6px);
    margin-bottom: 10px;
    border: 1px solid rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)
# --- Custom Styling ---
st.markdown("""
    <style>
    .trip-banner {
        background-color: #f5e3c3;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .trip-title {
        text-align: center;
        font-size: 24px;
        font-weight: bold;
    }
    .trip-subtitle {
        text-align: center;
        color: #555;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("🌍 Travel Assistant")

st.sidebar.subheader("🚗 Transport Options")

transport_modes = st.sidebar.multiselect(
    "Select Transport Modes",
    ["Flights ✈️", "Buses 🚌", "Trains 🚆"],
    default=["Flights ✈️"]
)
st.sidebar.subheader("⚙️ Personalize Your Trip")
# Budget Preference
budget_pref = st.sidebar.radio(
    "💰 Budget Preference",
    ["Economy", "Standard", "Luxury"]
)

# Flight Class
flight_class = st.sidebar.radio(
    "✈️ Flight Class",
    ["Economy", "Business", "First Class"]
)

# Hotel Rating
hotel_rating = st.sidebar.selectbox(
    "🏨 Preferred Hotel Rating",
    ["Any", "3 Star", "4 Star", "5 Star"]
)

# Packing Checklist
st.sidebar.subheader("🎒 Packing Checklist")
clothes = st.sidebar.checkbox("👕 Clothes", True)
shoes = st.sidebar.checkbox("👟 Comfortable Footwear", True)
sunglasses = st.sidebar.checkbox("🕶️ Sunglasses & Sunscreen")
book = st.sidebar.checkbox("📖 Travel Guidebook")
medicines= st.sidebar.checkbox("💊 Medications and First-aid")
# ---------------- HEADER ----------------
st.markdown('<div class="main-title">✈️ AI Travel Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Plan your dream trip with AI 🌍</div>', unsafe_allow_html=True)
# ---------------- MAIN INPUT ----------------
st.markdown("## 🌍 Where are you headed?")

col1, col2 = st.columns(2)

with col1:
   source = st.text_input("🛫 Departure City", "Karachi")

with col2:
    destination = st.text_input("🛬 Destination", "Lahore")


# ---------------- TRIP SETTINGS ----------------
st.markdown("## 📅 Plan Your Adventure")

days = st.slider("Trip Duration (days)", 1, 14, 5)

theme = st.selectbox(
    "🎯 Select Your Travel Theme",
    ["Adventure", "Relaxation", "Cultural", "Romantic", "Family", "Luxury"]
)

# --- Banner Section ---
st.markdown(f"""
<div class="trip-banner">
    <div class="trip-title">
        🌟 Your {theme} Trip from {source} to {destination} is about to begin! 🌟
    </div>
    <div class="trip-subtitle">
        Let's find the best flights, stays, and experiences for your unforgettable journey.
    </div>
</div>
""", unsafe_allow_html=True)

# --- Input Section ---
activities = st.text_input(
    "🌍 What activities do you enjoy?",
    placeholder="e.g., relaxing on the beach, exploring historical sites"
)

# --- Submit Button ---
if st.button("✔ Submit Preferences"):
    if activities:
        st.success(f"Preferences saved: {activities}")
        
        # You can store in session state
        st.session_state["activities"] = activities
    else:
        st.warning("Please enter your preferences first.")

# --- Date Inputs ---
col1, col2 = st.columns(2)

with col1:
    departure_date = st.date_input(
        "📅 Departure Date",
        min_value=date.today()
    )

with col2:
    return_date = st.date_input(
        "🔁 Return Date",
        min_value=departure_date if departure_date else date.today()
    )

# --- Validation ---
if departure_date and return_date:
    if return_date < departure_date:
        st.error("⚠️ Return date cannot be before departure date!")
    else:
        st.success(f"Trip: {departure_date} → {return_date}")
        st.session_state["departure_date"] = departure_date
        st.session_state["return_date"] = return_date
st.markdown(f"""
<div class="card">
    <h3>📍 Trip Overview</h3>
    <p><b>{source}</b> → <b>{destination}</b></p>
    <p>🗓 {days} Days | 🎯 {theme}</p>
</div>
""", unsafe_allow_html=True)

plan_button = st.button("🚀 Generate Travel Plan")

# ---------------- TRIP PLANNER ----------------
st.divider()

if plan_button:
    with st.spinner("🔍 Generating your AI travel plan..."):

        try:
            res = requests.post(
                f"{BACKEND_URL}/plan-trip",
                json={
                        "source": source,
                        "destination": destination,
                        "budget": 50000 if budget_pref == "Economy" else 100000 if budget_pref == "Standard" else 200000,
                        "days": days,
                        "trip_type": theme,
                        "flight_class": flight_class,
                        "hotel_rating": hotel_rating,
                        "budget_pref": budget_pref,
                        "transport_modes": transport_modes,
                        "departure_date": departure_date.strftime("%Y-%m-%d") if departure_date else None
                    }
            )

            data = res.json()

            st.success("✅ Trip Planned Successfully!")

            # -------- ITINERARY --------
            st.markdown("## 🗺️ Itinerary")
            st.write(data.get("itinerary", "No itinerary available"))

            #----------ROUTE--------------
            st.markdown("## 🛣️ Route Info")

            route = data.get("route", {})

            if route and route.get("distance_km") != "N/A":
                st.write(f"📏 Distance: {route.get('distance', 'N/A')}")
                st.write(f"✈️ Flight Time: {route.get('flight_time', 'N/A')}")
                st.write(f"🚆 Train Time: {route.get('train_time', 'N/A')}")
                st.write(f"🚌 Bus Time: {route.get('bus_time', 'N/A')}")
            else:
                st.write("Route info not available")
                if route.get("error"):
                     st.write(f"⚠️ {route.get('error')}")


            # -------- FLIGHTS --------
            st.markdown("## ✈️ Flights")

            flights = normalize_flights(data.get("flights", []))

            if flights:
                cols = st.columns(3)

                for i, f in enumerate(flights):
                    with cols[i % 3]:
                        
                        st.markdown(f"""
                            <div class="card">
                            <h3>{f.get('airline', 'Airline')}</h3>
                            <p>🛫 Departure: {f.get('departure', 'N/A')}</p>
                            <p>🛬 Arrival: {f.get('arrival', 'N/A')}</p>
                            <p>⏱️ Duration: {f.get('duration', 'N/A')}</p>
                            <h2>💰 {f.get('price', 'N/A')}</h2>
                
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No flights found")
            # -------- BUSES--------
            st.markdown("## 🚌 Buses")

            buses = data.get("buses", [])

            if buses:
                cols = st.columns(3)
                for i, b in enumerate(buses):
                    with cols[i % 3]:
                        st.markdown(f"""
                        <div class="card">
                        <h3>{b.get('operator')}</h3>
                        <p>🛫 {b.get('departure')}</p>
                        <p>🛬 {b.get('arrival')}</p>
                        <p>⏱️ {b.get('duration')}</p>
                        <h2>💰 {b.get('price')}</h2>
                    </div>
                    """, unsafe_allow_html=True)
            #----------TRAINS---------
            st.markdown("## 🚆 Trains")

            trains = data.get("trains", [])

            if trains:
                cols = st.columns(3)
                for i, t in enumerate(trains):
                    with cols[i % 3]:
                        st.markdown(f"""
                        <div class="card">
                        <h3>{t.get('train')}</h3>
                        <p>🛫 {t.get('departure')}</p>
                        <p>🛬 {t.get('arrival')}</p>
                        <p>⏱️ {t.get('duration')}</p>
                        <h2>💰 {t.get('price')}</h2>
                    </div>
                    """, unsafe_allow_html=True)
            # -------- HOTELS --------
            st.markdown("## 🏨 Hotels")

            hotels = data.get("hotels", [])

            if hotels:
                cols = st.columns(3)

                for i, h in enumerate(hotels):
                    with cols[i % 3]:
                        st.markdown(f"""
                            <div class="card">
                            <h3>{h.get('name', 'Hotel')}</h3>
                            <p>⭐ Rating: {h.get('rating', 'N/A')}</p>
                            <p>📍 {h.get('address', 'Address not available')}</p>
                            <h2>💰 {h.get('price', 'N/A')}</h2>
                        
                            </div>
                            """, unsafe_allow_html=True)
                

           # -------- WEATHER --------
            st.markdown("## 🌦️ 7-Day Weather Forecast")

            weather = data.get("weather", [])

            if isinstance(weather, list) and weather:
                cols = st.columns(len(weather[:7]))

                for i, day in enumerate(weather[:7]):
                    with cols[i]:
                        st.markdown(f"""
                        <div style="
                            text-align:center;
                            padding:15px;
                            border-radius:15px;
                            background: rgba(255,255,255,0.8);
                            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                        ">
                            <h4>{day.get("date")}</h4>
                            <h2>🌡️ {day.get("temp_day")}°C</h2>
                            <p>{day.get("desc")}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.write("Weather data not available")
            # -------- ATTRACTIONS --------
            st.markdown("## 📍 Attractions")
            attractions = data.get("attractions", [])
            if attractions:
                for a in attractions:
                    st.write(f"📌 {a.get('name')}")
            else:
                st.write("No attractions found")

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ---------------- CHAT SECTION ----------------
st.divider()
st.subheader("💬 Chat with AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask anything about your trip...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        res = requests.post(
            f"{BACKEND_URL}/chat",
            json={"message": user_input}
        )
        reply = res.json()["response"]
    except:
        reply = "⚠️ Backend not responding"

    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})


# ---------------- FOOTER ----------------
st.divider()
st.markdown("Made with ❤️ using FastAPI + AI | Smart Travel Planner 🌍")