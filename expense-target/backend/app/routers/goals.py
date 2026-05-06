from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud
from ..database import get_db

router = APIRouter(prefix="/goals", tags=["goals"])

@router.post("/", response_model=schemas.GoalResponse)
def create_goal(goal: schemas.GoalCreate, db: Session = Depends(get_db)):
    db_goal = crud.create_goal(db, goal, user_id=1)
    return enrich_goal(db_goal)

@router.get("/", response_model=List[schemas.GoalResponse])
def read_goals(active_only: bool = True, db: Session = Depends(get_db)):
    goals = crud.get_goals(db, user_id=1, active_only=active_only)
    return [enrich_goal(g) for g in goals]

@router.get("/{goal_id}", response_model=schemas.GoalResponse)
def read_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = crud.get_goal(db, goal_id, user_id=1)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return enrich_goal(goal)

@router.put("/{goal_id}", response_model=schemas.GoalResponse)
def update_goal(goal_id: int, goal: schemas.GoalUpdate, db: Session = Depends(get_db)):
    updated = crud.update_goal(db, goal_id, goal, user_id=1)
    if not updated:
        raise HTTPException(status_code=404, detail="Goal not found")
    return enrich_goal(updated)

@router.delete("/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    if not crud.delete_goal(db, goal_id, user_id=1):
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"message": "Goal deleted"}

def enrich_goal(goal):
    goal.percentage_complete = round((goal.current_amount / goal.target_amount * 100), 1) if goal.target_amount > 0 else 0
    return goal
