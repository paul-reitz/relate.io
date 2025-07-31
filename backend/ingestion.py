import pandas as pd
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

def import_clients_from_csv(csv_data: bytes):
    try:
        df = pd.read_csv(BytesIO(csv_data))
        required_columns = ['name', 'email', 'portfolio_value']
        if not all(col in df.columns for col in required_columns):
            raise ValueError("CSV must contain 'name', 'email', 'portfolio_value' columns")
        df['portfolio_value'] = pd.to_numeric(df['portfolio_value'], errors='coerce').fillna(0.0)
        records = df.to_dict(orient='records')
        from database import get_db_connection
        conn = get_db_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    for record in records:
                        cur.execute(
                            "INSERT INTO clients (name, email, portfolio_value) VALUES (%s, %s, %s) ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name, portfolio_value = EXCLUDED.portfolio_value",
                            (record['name'], record['email'], record['portfolio_value'])
                        )
            return records
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Error in CSV import: {e}")
        raise