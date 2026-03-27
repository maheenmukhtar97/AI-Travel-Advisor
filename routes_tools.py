import requests

CITY_COORDS = {
    "karachi": (24.8607, 67.0011),
    "lahore": (31.5204, 74.3587),
    "islamabad": (33.6844, 73.0479)
}

def get_route(source, destination):
    source = source.lower()
    destination = destination.lower()

    if source not in CITY_COORDS or destination not in CITY_COORDS:
        return {"distance_km": "N/A", "duration_hr": "N/A", "error": "City not supported"}

    src_lat, src_lon = CITY_COORDS[source]
    dst_lat, dst_lon = CITY_COORDS[destination]

    url = f"http://router.project-osrm.org/route/v1/driving/{src_lon},{src_lat};{dst_lon},{dst_lat}?overview=false"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return {"distance_km": "N/A", "duration_hr": "N/A", "error": f"HTTP {response.status_code}"}

        data = response.json()  # <-- safely parse JSON
        if "routes" not in data or not data["routes"]:
            return {"distance_km": "N/A", "duration_hr": "N/A", "error": "No route found"}

        route = data["routes"][0]

        distance_km = route["distance"] / 1000
        duration_hr = route["duration"] / 3600

        return {
            "distance_km": round(distance_km, 2),
            "duration_hr": round(duration_hr, 2)
        }

    except requests.exceptions.RequestException as e:
        # Any network or timeout error
        return {"distance_km": "N/A", "duration_hr": "N/A", "error": str(e)}
    except ValueError as e:
        # JSON decode error
        return {"distance_km": "N/A", "duration_hr": "N/A", "error": f"Invalid JSON: {e}"}