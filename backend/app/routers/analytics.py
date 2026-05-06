from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta
from .. import crud
from ..database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    user_id = 1
    today = date.today()
    month_start = today.replace(day=1)
    from sqlalchemy import func, extract
    from ..models import Expense
    
    monthly_income = db.query(func.sum(Expense.amount)).filter(
        Expense.user_id == user_id, Expense.is_income == True,
        extract('month', Expense.date) == today.month,
        extract('year', Expense.date) == today.year
    ).scalar() or 0
    
    monthly_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.user_id == user_id, Expense.is_income == False,
        extract('month', Expense.date) == today.month,
        extract('year', Expense.date) == today.year
    ).scalar() or 0
    
    savings = monthly_income - monthly_expenses
    savings_rate = (savings / monthly_income * 100) if monthly_income > 0 else 0
    
    top_categories = db.query(Expense.category, func.sum(Expense.amount).label("total")).filter(
        Expense.user_id == user_id, Expense.is_income == False, Expense.date >= month_start
    ).group_by(Expense.category).order_by(func.sum(Expense.amount).desc()).limit(5).all()
    
    recent = crud.get_expenses(db, user_id, limit=5)
    budget_status = crud.get_budget_status(db, user_id)
    alerts = [b for b in budget_status if b["alert"]]
    
    recurring_items = crud.get_recurring(db, user_id)
    upcoming = []
    for item in recurring_items:
        if item.next_due_date <= today + timedelta(days=7):
            upcoming.append({"name": item.name, "amount": item.amount, "due_date": item.next_due_date, "days_until": (item.next_due_date - today).days})
    
    return {
        "total_balance": float(monthly_income - monthly_expenses),
        "monthly_income": float(monthly_income),
        "monthly_expenses": float(monthly_expenses),
        "monthly_savings": float(savings),
        "savings_rate": round(float(savings_rate), 1),
        "top_categories": [{"category": c.category, "amount": float(c.total)} for c in top_categories],
        "recent_transactions": recent,
        "budget_alerts": alerts,
        "upcoming_bills": sorted(upcoming, key=lambda x: x["due_date"])
    }

@router.get("/monthly-trend")
def get_monthly_trend(months: int = 6, db: Session = Depends(get_db)):
    return crud.get_monthly_summary(db, 1, months)

@router.get("/category-breakdown")
def get_category_breakdown(db: Session = Depends(get_db)):
    from sqlalchemy import func
    from ..models import Expense
    start = date.today().replace(day=1)
    results = db.query(Expense.category, func.sum(Expense.amount).label("total"), func.count(Expense.id).label("count")).filter(
        Expense.user_id == 1, Expense.is_income == False, Expense.date >= start
    ).group_by(Expense.category).all()
    return [{"category": r.category, "total": float(r.total), "count": r.count} for r in results]
