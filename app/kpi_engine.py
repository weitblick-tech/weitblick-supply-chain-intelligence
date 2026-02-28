import pandas as pd

def calculate_kpis(df: pd.DataFrame):
    total_shipments = len(df)
    on_time_rate = (df['on_time'].sum() / total_shipments) * 100
    avg_delay = df['delay_hours'].mean()
    total_revenue = df['revenue'].sum()
    total_cost = df['shipment_cost'].sum()
    total_profit = df['profit'].sum()

    return {
        "total_shipments": total_shipments,
        "on_time_rate": round(on_time_rate, 2),
        "avg_delay": round(avg_delay, 2),
        "total_revenue": round(total_revenue, 2),
        "total_cost": round(total_cost, 2),
        "total_profit": round(total_profit, 2)
    }