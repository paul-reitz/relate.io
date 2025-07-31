from celery.schedules import crontab

broker_url = 'redis://localhost:6379/0'
beat_schedule = {
    'weekly-updates': {
        'task': 'tasks.send_weekly_update',
        'schedule': crontab(minute=0, hour=0, day_of_week='mon'),  # Weekly on Monday
        'args': (1,)  # Example client_id; query DB in real
    },
}
