from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta
from .. import schemas, crud
from ..database import get_db

router = APIRouter(prefix="/recurring", tags=["recurring"])

@router.post("/", response_model=schemas.RecurringResponse)
def create_recurring(recurring: schemas.RecurringCreate, db: Session = Depends(get_db)):
    return crud.create_recurring(db, recurring, user_id=1)

@router.get("/", response_model=List[schemas.RecurringResponse])
def read_recurring(db: Session = Depends(get_db)):
    return crud.get_recurring(db, user_id=1)

@router.get("/upcoming")
def get_upcoming_bills(days: int = 30, db: Session = Depends(get_db)):
    today = date.today()
    end_date = today + timedelta(days=days)
    items = crud.get_recurring(db, user_id=1)
    upcoming = []
    for item in items:
        if today <= item.next_due_date <= end_date:
            upcoming.append({"id": item.id, "name": item.name, "amount": item.amount, "category": item.category, "due_date": item.next_due_date, "days_until": (item.next_due_date - today).days})
    return sorted(upcoming, key=lambda x: x["due_date"])

@router.delete("/{recurring_id}")
def delete_recurring(recurring_id: int, db: Session = Depends(get_db)):
    if crud.delete_recurring(db, recurring_id, user_id=1):
        return {"message": "Deleted"}
    return {"error": "Not found"}
