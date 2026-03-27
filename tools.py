# tools.py

def route_planner(source: str, destination: str):
    if source == "Lahore" and destination == "Karachi":
        return {
            "distance": "1200 km",
            "flight_time": "1.5 hours",
            "train_time": "18 hours",
            "bus_time": "20 hours"
        }
    else:
        return {"error": "Route not supported"}

def ticket_suggestions(mode: str):
    data = {
        "flight": {
            "price": 18000,
            "departure": "10:00 AM",
            "arrival": "11:30 AM"
        },
        "train": {
            "price": 5000,
            "departure": "5:00 PM",
            "arrival": "11:00 AM (next day)"
        },
        "bus": {
            "price": 4500,
            "departure": "8:00 PM",
            "arrival": "4:00 PM (next day)"
        }
    }

    return data.get(mode.lower(), {"error": "Invalid mode"})

def hotel_recommendations(budget: int):
    hotels = [
        {"name": "Avari Towers", "price_per_night": 15000, "rating": 4.5},
        {"name": "Pearl Continental", "price_per_night": 20000, "rating": 4.7},
        {"name": "Hotel One", "price_per_night": 8000, "rating": 4.0},
    ]

    filtered = [h for h in hotels if h["price_per_night"] <= budget]
    return filtered
