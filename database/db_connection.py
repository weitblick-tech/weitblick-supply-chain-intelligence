from psycopg_pool import ConnectionPool
import logging
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
logger = logging.getLogger(__name__)

def configure_connection(conn):
    """
    Runs once when a new connection is created.
    FIX: Must commit to avoid INTRANS state in psycopg_pool
    """
    with conn.cursor() as cur:
        cur.execute("SET search_path TO wb_int_prd")
        cur.execute("SET statement_timeout TO 30000")
        cur.execute("SET idle_in_transaction_session_timeout TO 30000")
    
    conn.commit()

POOL = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=3,  
    timeout=10,
    max_idle=60,  
    reconnect_timeout=10,
    configure=configure_connection,
    kwargs={
        "autocommit": False,
        "connect_timeout": 5,
        "sslmode": "require",
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    },
)

def get_connection():
    return POOL.connection()

"""
usage: - 

def fetch_users():
    with POOL.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users")
            return cur.fetchall()
"""