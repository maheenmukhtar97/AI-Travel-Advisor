import requests
import os
from dotenv import load_dotenv
import datetime
from datetime import datetime, timedelta

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")


# Optional: map city names to lat/lon for faster queries
CITY_COORDS = {
    "lahore": {"lat": 31.5497, "lon": 74.3436},
    "karachi": {"lat": 24.8607, "lon": 67.0011},
    "islamabad": {"lat": 33.6844, "lon": 73.0479},
    "peshawar": {"lat": 34.0151, "lon": 71.5249},
    "quetta": {"lat": 30.1798, "lon": 66.9750}
}

def get_weather(city: str):
    city_lower = city.lower().strip()
    
    # Get coordinates
    coords = CITY_COORDS.get(city_lower)
    if not coords:
        return {"error": f"City '{city}' not supported for weather."}

    lat, lon = coords["lat"], coords["lon"]

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
    "lat": lat,
    "lon": lon,
    "units": "metric",
    "appid": API_KEY
    }
    try:
        res = requests.get(url, params=params, timeout=5)
        res.raise_for_status()
        data = res.json()

        daily_forecasts = []

        data_list = data.get("list", [])

        for i in range(0, len(data_list), 8):  # every 24 hours (3hr * 8)
            day_data = data_list[i]

            date = day_data.get("dt_txt", "").split(" ")[0]
            temp_day = day_data.get("main", {}).get("temp", "N/A")
            temp_night = temp_day  # fallback
            desc = day_data.get("weather", [{}])[0].get("description", "")

            daily_forecasts.append({
                "date": date,
                "temp_day": temp_day,
                "temp_night": temp_night,
                "desc": desc.title()
            })

        return daily_forecasts[:7]

    except Exception as e:
        print("Weather API Error:", e)
        return {"error": "Weather data not available"}
    
print("API KEY:", API_KEY)