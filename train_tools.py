def get_trains(source, destination):
    if source.lower() == "lahore" and destination.lower() == "karachi":
        return [
            {
                "train": "Green Line Express",
                "departure": "08:00 PM",
                "arrival": "02:00 PM",
                "duration": "18h",
                "price": 7000
            },
            {
                "train": "Karachi Express",
                "departure": "05:00 PM",
                "arrival": "11:00 AM",
                "duration": "18h",
                "price": 6500
            }
        ]

    # Default
    return [
        {
            "train": "Karakoram Express",
            "departure": "03:00 PM",
            "arrival": "01:00 AM",
            "duration": "10h",
            "price": 4500
        },
        {
            "train": "Allama Iqbal Express",
            "departure": "12:00 PM",
            "arrival": "10:00 PM",
            "duration": "10h",
            "price": 4200
        }

    ]