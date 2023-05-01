from datetime import date, timedelta
import random
import time
import string
from app.db.base import SessionLocal
from app.models import models


API_RECORDS_TO_RETURN: int = 5
API_TIME_DELAY: float = 0.1  # seconds


def generate_user(task_id: int, start_date: date):
    name = "".join(random.sample(string.ascii_letters, 10))
    user = models.User(
        task_id=task_id,
        full_name=name,
        email=f"{name}@example.com",
        created_at=start_date
    )
    return user

def generate_country(user_id: int, created_at: date):
    code = random.choice(["GB", "FR", "IT"])
    return models.Country(
        user_id=user_id, country_id=code, created_at=created_at
    )

def call_remote_api(db: SessionLocal, task_id: int, start_date: date):
    time.sleep(API_TIME_DELAY)
    for i in range(API_RECORDS_TO_RETURN):
        user_db = generate_user(task_id, start_date)
        db.add(user_db)
        db.commit()
        db.refresh(user_db)
        db.add(generate_country(user_db.id, start_date))

def start_downloading_leads(task_id: int, start_date: date, end_date: date):
    db = SessionLocal()
    try:
        task = db.query(models.Task).filter_by(id=task_id).one()
        task.status = "RUNNING"
        db.commit()

        while start_date <= end_date:
            call_remote_api(db, task_id, start_date)
            start_date += timedelta(days=1)

        task.status = "SUCCESFULL"
        db.commit()
    finally:
        db.close()
