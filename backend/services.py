from ai import generate_narrative, analyze_feedback
from messaging import send_email_update
from database import get_db_connection
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

def generate_and_send_update(client_id: int):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name, email, portfolio_value FROM clients WHERE id = %s", (client_id,))
                client = cur.fetchone()
        if not client:
            raise HTTPException(404, "Client not found")
        data = {"pnl": 5.2, "top_holdings": ["AAPL", "GOOG"]}  # Mock; replace with real data
        narrative = generate_narrative(data)
        send_email_update(client[1], narrative, client_id)
    finally:
        conn.close()

def submit_feedback(client_id: int, text: str):
    sentiment = analyze_feedback(text)
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO feedback (client_id, text, sentiment) VALUES (%s, %s, %s)",
                    (client_id, text, sentiment)
                )
        return sentiment
    finally:
        conn.close()

def get_clients():
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, email, portfolio_value FROM clients")
                clients = cur.fetchall()
        return [{"id": c[0], "name": c[1], "email": c[2], "portfolio_value": c[3]} for c in clients]
    finally:
        conn.close()

def get_feedback():
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, client_id, text, sentiment FROM feedback")
                feedbacks = cur.fetchall()
        return [{"id": f[0], "client_id": f[1], "text": f[2], "sentiment": f[3]} for f in feedbacks]
    finally:
        conn.close()