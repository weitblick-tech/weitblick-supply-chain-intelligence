def generate_insights(df):
    insights = []

    most_delayed_mode = df.groupby("transport_mode")["delay_hours"].mean().idxmax()
    insights.append(f"🚚 {most_delayed_mode} transport shows the highest average delays.")

    top_route = df.groupby("origin_city")["revenue"].sum().idxmax()
    insights.append(f"💰 Shipments originating from {top_route} generate the highest revenue.")

    high_cost_city = df.groupby("destination_city")["shipment_cost"].mean().idxmax()
    insights.append(f"📉 Deliveries to {high_cost_city} have the highest average shipment cost.")

    delay_rate = (df['delay_hours'] > 0).mean() * 100
    insights.append(f"⏱️ {round(delay_rate,2)}% of shipments are experiencing delays.")

    return insights