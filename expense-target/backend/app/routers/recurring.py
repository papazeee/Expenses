from fastapi import APIRouter, Depends, HTTPException
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
def read_recurring(active_only: bool = True, db: Session = Depends(get_db)):
    return crud.get_recurring(db, user_id=1, active_only=active_only)

@router.get("/upcoming")
def get_upcoming_bills(days: int = 30, db: Session = Depends(get_db)):
    today = date.today()
    end_date = today + timedelta(days=days)
    
    items = crud.get_recurring(db, user_id=1, active_only=True)
    upcoming = []
    
    for item in items:
        if today <= item.next_due_date <= end_date:
            upcoming.append({
                "id": item.id,
                "name": item.name,
                "amount": item.amount,
                "category": item.category,
                "due_date": item.next_due_date,
                "days_until": (item.next_due_date - today).days
            })
    
    return sorted(upcoming, key=lambda x: x["due_date"])

@router.put("/{recurring_id}", response_model=schemas.RecurringResponse)
def update_recurring(recurring_id: int, data: dict, db: Session = Depends(get_db)):
    updated = crud.update_recurring(db, recurring_id, data, user_id=1)
    if not updated:
        raise HTTPException(status_code=404, detail="Not found")
    return updated

@router.delete("/{recurring_id}")
def delete_recurring(recurring_id: int, db: Session = Depends(get_db)):
    if not crud.delete_recurring(db, recurring_id, user_id=1):
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Deleted"}
