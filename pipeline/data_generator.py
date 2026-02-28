import pandas as pd
import random
from datetime import datetime, timedelta
import os

os.makedirs("data/raw", exist_ok=True)

cities = ["Mumbai", "Dubai", "Singapore", "London", "New York", "Sydney"]
transport_modes = ["Air", "Sea", "Truck"]
statuses = ["In Transit", "Delivered", "Delayed"]

def generate_shipment():
    origin = random.choice(cities)
    destination = random.choice([c for c in cities if c != origin])

    shipment_date = datetime.now() - timedelta(days=random.randint(1, 7))
    delay = random.choice([0, random.randint(2, 48)])

    status = "Delayed" if delay > 0 else random.choice(statuses)

    return {
        "origin_city": origin,
        "destination_city": destination,
        "shipment_date": shipment_date,
        "delivery_date": shipment_date + timedelta(days=random.randint(2, 10)),
        "status": status,
        "delay_hours": delay,
        "transport_mode": random.choice(transport_modes),
        "fuel_cost": round(random.uniform(100, 800), 2),
        "shipment_cost": round(random.uniform(500, 3000), 2),
        "revenue": round(random.uniform(3000, 7000), 2),
    }

def generate_data(n=100):
    data = [generate_shipment() for _ in range(n)]
    df = pd.DataFrame(data)
    df.to_csv("data/raw/shipments.csv", index=False)
    print("Real-time shipment data generated!")

if __name__ == "__main__":
    generate_data(200)