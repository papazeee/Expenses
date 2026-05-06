from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    category: str
    date: date
    is_income: bool = False
    payment_method: Optional[str] = "cash"

    class Config:
        orm_mode = True

class ExpenseResponse(ExpenseCreate):
    id: int
    created_at: datetime
    user_id: int

    class Config:
        orm_mode = True

class BudgetCreate(BaseModel):
    category: str
    amount: float = Field(..., gt=0)
    alert_threshold: float = Field(80.0, ge=0, le=100)
    start_date: date
    period: str = "monthly"

    class Config:
        orm_mode = True

class BudgetResponse(BudgetCreate):
    id: int
    is_active: bool
    user_id: int
    spent: Optional[float] = 0.0
    remaining: Optional[float] = 0.0
    percentage_used: Optional[float] = 0.0

    class Config:
        orm_mode = True

class GoalCreate(BaseModel):
    name: str
    target_amount: float = Field(..., gt=0)
    current_amount: float = 0.0
    deadline: Optional[date] = None
    category: Optional[str] = "savings"
    color: Optional[str] = "#3b82f6"

    class Config:
        orm_mode = True

class GoalResponse(GoalCreate):
    id: int
    is_active: bool
    user_id: int
    percentage_complete: Optional[float] = 0.0

    class Config:
        orm_mode = True

class RecurringCreate(BaseModel):
    name: str
    amount: float = Field(..., gt=0)
    category: str
    frequency: str
    start_date: date
    next_due_date: date
    auto_pay: bool = False
    payment_method: Optional[str] = None

    class Config:
        orm_mode = True

class RecurringResponse(RecurringCreate):
    id: int
    is_active: bool
    user_id: int

    class Config:
        orm_mode = True
