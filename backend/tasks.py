from celery import Celery
from celery.schedules import crontab
import logging

from services import generate_and_send_update

logger = logging.getLogger(__name__)

app = Celery('tasks', broker='redis://localhost:6379/0')

app.conf.beat_schedule = {
    'weekly-updates': {
        'task': 'tasks.send_weekly_updates',
        'schedule': crontab(minute='*/1'),  # Every minute for testing; change to crontab(day_of_week='mon') for weekly
    },
}

@app.task
def send_weekly_updates():
    from database import get_db_connection
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM clients")
                clients = cur.fetchall()
        for client_id in [c[0] for c in clients]:
            try:
                generate_and_send_update(client_id)
                logger.info(f"Weekly update sent for client {client_id}")
            except Exception as e:
                logger.error(f"Failed to send weekly update for {client_id}: {e}")
    finally:
        conn.close()