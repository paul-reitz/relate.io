import psycopg2
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        return psycopg2.connect(
            dbname=os.getenv("DB_NAME", "relate_io"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "password"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def create_tables():
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS clients (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255),
                        email VARCHAR(255) UNIQUE,
                        portfolio_value FLOAT
                    );
                    CREATE TABLE IF NOT EXISTS feedback (
                        id SERIAL PRIMARY KEY,
                        client_id INTEGER REFERENCES clients(id),
                        text TEXT,
                        sentiment VARCHAR(50)
                    );
                """)
    finally:
        conn.close()