from fastapi import APIRouter, Depends
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

@router.delete("/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    if crud.delete_budget(db, budget_id, user_id=1):
        return {"message": "Deleted"}
    return {"error": "Not found"}

def enrich_budget(db, budget):
    status = crud.get_budget_status(db, 1)
    for s in status:
        if s["id"] == budget.id:
            budget.spent = s["spent"]
            budget.remaining = s["remaining"]
            budget.percentage_used = s["percentage_used"]
            break
    return budget
