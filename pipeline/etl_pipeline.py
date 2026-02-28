import pandas as pd
from database.db_connection import get_connection

SCHEMA = "wb_int_prd"
TABLE = "shipments"

def run_etl():
    df = pd.read_csv("data/raw/shipments.csv")

    if df.empty:
        print("CSV is empty. No data to load.")
        return

    df['shipment_date'] = pd.to_datetime(df['shipment_date'])
    df['delivery_date'] = pd.to_datetime(df['delivery_date'])
    df['profit'] = df['revenue'] - df['shipment_cost']
    df['on_time'] = (df['delay_hours'] == 0).astype(int)

    print(f"Loaded {len(df)} records from CSV")

    insert_query = f"""
    INSERT INTO {SCHEMA}.{TABLE} (
        origin_city,
        destination_city,
        shipment_date,
        delivery_date,
        status,
        delay_hours,
        transport_mode,
        fuel_cost,
        shipment_cost,
        revenue,
        profit,
        on_time
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    data_tuples = list(df[[
        "origin_city",
        "destination_city",
        "shipment_date",
        "delivery_date",
        "status",
        "delay_hours",
        "transport_mode",
        "fuel_cost",
        "shipment_cost",
        "revenue",
        "profit",
        "on_time"
    ]].itertuples(index=False, name=None))

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE {SCHEMA}.{TABLE};")
            cur.executemany(insert_query, data_tuples)

        conn.commit()

    print("✅ ETL completed and bulk data loaded successfully!")


if __name__ == "__main__":
    from database.db_connection import POOL
    try:
        run_etl()
    except Exception as e:
        print(f"ETL failed: {e}")
        raise
    finally:
        POOL.close()
        print("DB pool closed.")