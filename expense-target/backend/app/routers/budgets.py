from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud
from ..database import get_db

router = APIRouter(prefix="/budgets", tags=["budgets"])

@router.post("/", response_model=schemas.BudgetResponse)
def create_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_db)):
    db_budget = crud.create_budget(db, budget, user_id=1)
    return enrich_budget(db, db_budget)

@router.get("/", response_model=List[schemas.BudgetResponse])
def read_budgets(db: Session = Depends(get_db)):
    budgets = crud.get_budgets(db, user_id=1)
    return [enrich_budget(db, b) for b in budgets]

@router.get("/{budget_id}", response_model=schemas.BudgetResponse)
def read_budget(budget_id: int, db: Session = Depends(get_db)):
    budget = crud.get_budget(db, budget_id, user_id=1)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return enrich_budget(db, budget)

@router.put("/{budget_id}", response_model=schemas.BudgetResponse)
def update_budget(budget_id: int, budget_data: dict, db: Session = Depends(get_db)):
    updated = crud.update_budget(db, budget_id, budget_data, user_id=1)
    if not updated:
        raise HTTPException(status_code=404, detail="Budget not found")
    return enrich_budget(db, updated)

@router.delete("/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    if not crud.delete_budget(db, budget_id, user_id=1):
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"message": "Budget deleted"}

def enrich_budget(db, budget):
    status = crud.get_budget_status(db, 1)
    for s in status:
        if s["id"] == budget.id:
            budget.spent = s["spent"]
            budget.remaining = s["remaining"]
            budget.percentage_used = s["percentage_used"]
            break
    return budget
