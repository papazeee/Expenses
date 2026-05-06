from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud
from ..database import get_db

router = APIRouter(prefix="/goals", tags=["goals"])

@router.post("/", response_model=schemas.GoalResponse)
def create_goal(goal: schemas.GoalCreate, db: Session = Depends(get_db)):
    db_goal = crud.create_goal(db, goal, user_id=1)
    db_goal.percentage_complete = round((db_goal.current_amount / db_goal.target_amount * 100), 1) if db_goal.target_amount > 0 else 0
    return db_goal

@router.get("/", response_model=List[schemas.GoalResponse])
def read_goals(db: Session = Depends(get_db)):
    goals = crud.get_goals(db, user_id=1)
    for g in goals:
        g.percentage_complete = round((g.current_amount / g.target_amount * 100), 1) if g.target_amount > 0 else 0
    return goals

@router.delete("/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    if crud.delete_goal(db, goal_id, user_id=1):
        return {"message": "Deleted"}
    return {"error": "Not found"}
