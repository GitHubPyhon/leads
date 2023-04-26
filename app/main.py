from datetime import date, datetime
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.models import models
from app.schemas import schemas
from app.db.base import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/leads/", response_model=list[schemas.Lead])
def read_users(
        start_date: date = datetime.utcnow(),
        end_date: date = datetime.utcnow(),
        db: Session = Depends(get_db)
):
    leads = db.query(models.Lead).filter(
        models.Lead.created_at > start_date,
        models.Lead.created_at < end_date
    ).all()
    return leads


@app.post("/leads/", response_model=schemas.CreateLead)
def read_users(lead: schemas.CreateLead, db: Session = Depends(get_db)):
    db_lead = models.Lead(**lead.dict())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return lead
