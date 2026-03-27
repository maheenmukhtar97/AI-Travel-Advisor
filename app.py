import streamlit as st
import requests

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AI Travel Planner ✈️",
    page_icon="🌍",
    layout="wide"
)

BACKEND_URL = "http://127.0.0.1:8000"

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
# ---------------- SIDEBAR ----------------
st.sidebar.title("🌍 Travel Assistant")

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
                    "trip_type": theme
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
                st.write(f"📏 Distance: {route.get('distance_km')} km")
                st.write(f"⏱️ Travel Time: {route.get('duration_hr')} hours")
            else:
                st.write("Route info not available")
                if route.get("error"):
                     st.write(f"⚠️ {route.get('error')}")


            # -------- FLIGHTS --------
            st.markdown("## ✈️ Flights")
            flights = data.get("flights", [])
            if flights:
                for f in flights:
                    st.info(f"{f.get('airline')} | 💰 {f.get('price')}")
            else:
                st.write("No flights found")

            # -------- HOTELS --------
            st.markdown("## 🏨 Hotels")
            hotels = data.get("hotels", [])
            if hotels:
                for h in hotels:
                    st.success(f"{h.get('name')} | 💰 {h.get('price')}")
            else:
                st.write("No hotels found")

           # -------- WEATHER --------
            st.markdown("## 🌦️ 7-Day Weather Forecast")

            weather = data.get("weather", [])

            if isinstance(weather, list) and weather:
                cols = st.columns(len(weather[:7]))

                for i, day in enumerate(weather[:7]):
                    with cols[i]:
                        st.markdown(f"""
                        <div class="card">
                            <h4>{day.get("date", "Date")}</h4>
                            <p>🌡️ Day: {day.get("temp_day", "N/A")}°C / Night: {day.get("temp_night", "N/A")}°C</p>
                            <p>{day.get("desc", "")}</p>
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