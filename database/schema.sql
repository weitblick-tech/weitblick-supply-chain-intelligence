CREATE TABLE IF NOT EXISTS shipments (
    shipment_id SERIAL PRIMARY KEY,
    origin_city VARCHAR(50),
    destination_city VARCHAR(50),
    shipment_date TIMESTAMP,
    delivery_date TIMESTAMP,
    status VARCHAR(20),
    delay_hours FLOAT,
    transport_mode VARCHAR(20),
    fuel_cost FLOAT,
    shipment_cost FLOAT,
    revenue FLOAT
);