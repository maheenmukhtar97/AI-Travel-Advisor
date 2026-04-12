def get_buses(source, destination):
    if source.lower() == "lahore" and destination.lower() == "karachi":
        return [
            {
                "operator": "Daewoo Express",
                "departure": "06:00 PM",
                "arrival": "10:00 AM",
                "duration": "16h",
                "price": 6500
            },
            {
                "operator": "Faisal Movers",
                "departure": "08:00 PM",
                "arrival": "12:00 PM",
                "duration": "16h",
                "price": 6000
            }
        ]

    # Default (Karachi → Lahore)
    return [
        {
            "operator": "Daewoo Express",
            "departure": "08:00 AM",
            "arrival": "02:00 PM",
            "duration": "6h",
            "price": 6500
        },
        {
            "operator": "Bilal Travels",
            "departure": "01:00 PM",
            "arrival": "07:00 PM",
            "duration": "6h",
            "price": 5000
        }

    ]
