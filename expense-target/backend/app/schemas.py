from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    category: str
    date: date
    is_income: bool = False
    payment_method: Optional[str] = "cash"
    tags: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = None
    date: Optional[date] = None
    is_income: Optional[bool] = None
    payment_method: Optional[str] = None
    tags: Optional[str] = None

class ExpenseResponse(ExpenseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    
    class Config:
        from_attributes = True

class BudgetBase(BaseModel):
    category: str
    amount: float = Field(..., gt=0)
    period: str = "monthly"
    alert_threshold: float = Field(80.0, ge=0, le=100)
    start_date: date
    end_date: Optional[date] = None

class BudgetCreate(BudgetBase):
    pass

class BudgetResponse(BudgetBase):
    id: int
    is_active: bool
    user_id: int
    spent: Optional[float] = 0.0
    remaining: Optional[float] = 0.0
    percentage_used: Optional[float] = 0.0
    
    class Config:
        from_attributes = True

class GoalBase(BaseModel):
    name: str
    target_amount: float = Field(..., gt=0)
    current_amount: float = 0.0
    deadline: Optional[date] = None
    category: Optional[str] = "savings"
    color: Optional[str] = "#3b82f6"

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    deadline: Optional[date] = None
    is_active: Optional[bool] = None

class GoalResponse(GoalBase):
    id: int
    is_active: bool
    created_at: datetime
    user_id: int
    percentage_complete: Optional[float] = 0.0
    
    class Config:
        from_attributes = True

class RecurringBase(BaseModel):
    name: str
    amount: float = Field(..., gt=0)
    category: str
    frequency: str
    start_date: date
    end_date: Optional[date] = None
    next_due_date: date
    auto_pay: bool = False
    payment_method: Optional[str] = None

class RecurringCreate(RecurringBase):
    pass

class RecurringResponse(RecurringBase):
    id: int
    is_active: bool
    user_id: int
    
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_balance: float
    monthly_income: float
    monthly_expenses: float
    monthly_savings: float
    savings_rate: float
    top_categories: List[dict]
    recent_transactions: List[ExpenseResponse]
    budget_alerts: List[dict]
    upcoming_bills: List[dict]

class MonthlyData(BaseModel):
    month: str
    income: float
    expenses: float
    savings: float

class AnalyticsResponse(BaseModel):
    monthly_trend: List[MonthlyData]
    category_breakdown: List[dict]
    spending_by_day: List[dict]
    budget_vs_actual: List[dict]
