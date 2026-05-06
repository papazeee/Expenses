from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_, or_
from datetime import datetime, date, timedelta
from typing import List, Optional
from . import models, schemas

# Expense CRUD
def create_expense(db: Session, expense: schemas.ExpenseCreate, user_id: int):
    db_expense = models.Expense(**expense.model_dump(), user_id=user_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expenses(db: Session, user_id: int, skip: int = 0, limit: int = 100, 
                 category: Optional[str] = None, start_date: Optional[date] = None,
                 end_date: Optional[date] = None, search: Optional[str] = None):
    query = db.query(models.Expense).filter(models.Expense.user_id == user_id)
    
    if category:
        query = query.filter(models.Expense.category == category)
    if start_date:
        query = query.filter(models.Expense.date >= start_date)
    if end_date:
        query = query.filter(models.Expense.date <= end_date)
    if search:
        query = query.filter(models.Expense.description.ilike(f"%{search}%"))
    
    return query.order_by(models.Expense.date.desc()).offset(skip).limit(limit).all()

def get_expense(db: Session, expense_id: int, user_id: int):
    return db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == user_id
    ).first()

def update_expense(db: Session, expense_id: int, expense: schemas.ExpenseUpdate, user_id: int):
    db_expense = get_expense(db, expense_id, user_id)
    if not db_expense:
        return None
    
    update_data = expense.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_expense, field, value)
    
    db.commit()
    db.refresh(db_expense)
    return db_expense

def delete_expense(db: Session, expense_id: int, user_id: int):
    db_expense = get_expense(db, expense_id, user_id)
    if db_expense:
        db.delete(db_expense)
        db.commit()
        return True
    return False

# Budget CRUD
def create_budget(db: Session, budget: schemas.BudgetCreate, user_id: int):
    db_budget = models.Budget(**budget.model_dump(), user_id=user_id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def get_budgets(db: Session, user_id: int):
    return db.query(models.Budget).filter(
        models.Budget.user_id == user_id,
        models.Budget.is_active == True
    ).all()

def get_budget(db: Session, budget_id: int, user_id: int):
    return db.query(models.Budget).filter(
        models.Budget.id == budget_id,
        models.Budget.user_id == user_id
    ).first()

def update_budget(db: Session, budget_id: int, budget_data: dict, user_id: int):
    db_budget = get_budget(db, budget_id, user_id)
    if not db_budget:
        return None
    
    for field, value in budget_data.items():
        setattr(db_budget, field, value)
    
    db.commit()
    db.refresh(db_budget)
    return db_budget

def delete_budget(db: Session, budget_id: int, user_id: int):
    db_budget = get_budget(db, budget_id, user_id)
    if db_budget:
        db.delete(db_budget)
        db.commit()
        return True
    return False

# Goal CRUD
def create_goal(db: Session, goal: schemas.GoalCreate, user_id: int):
    db_goal = models.Goal(**goal.model_dump(), user_id=user_id)
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

def get_goals(db: Session, user_id: int, active_only: bool = True):
    query = db.query(models.Goal).filter(models.Goal.user_id == user_id)
    if active_only:
        query = query.filter(models.Goal.is_active == True)
    return query.all()

def get_goal(db: Session, goal_id: int, user_id: int):
    return db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == user_id
    ).first()

def update_goal(db: Session, goal_id: int, goal: schemas.GoalUpdate, user_id: int):
    db_goal = get_goal(db, goal_id, user_id)
    if not db_goal:
        return None
    
    update_data = goal.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_goal, field, value)
    
    db.commit()
    db.refresh(db_goal)
    return db_goal

def delete_goal(db: Session, goal_id: int, user_id: int):
    db_goal = get_goal(db, goal_id, user_id)
    if db_goal:
        db.delete(db_goal)
        db.commit()
        return True
    return False

# Recurring CRUD
def create_recurring(db: Session, recurring: schemas.RecurringCreate, user_id: int):
    db_recurring = models.RecurringExpense(**recurring.model_dump(), user_id=user_id)
    db.add(db_recurring)
    db.commit()
    db.refresh(db_recurring)
    return db_recurring

def get_recurring(db: Session, user_id: int, active_only: bool = True):
    query = db.query(models.RecurringExpense).filter(models.RecurringExpense.user_id == user_id)
    if active_only:
        query = query.filter(models.RecurringExpense.is_active == True)
    return query.order_by(models.RecurringExpense.next_due_date).all()

def get_recurring_item(db: Session, recurring_id: int, user_id: int):
    return db.query(models.RecurringExpense).filter(
        models.RecurringExpense.id == recurring_id,
        models.RecurringExpense.user_id == user_id
    ).first()

def update_recurring(db: Session, recurring_id: int, data: dict, user_id: int):
    db_item = get_recurring_item(db, recurring_id, user_id)
    if not db_item:
        return None
    
    for field, value in data.items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_recurring(db: Session, recurring_id: int, user_id: int):
    db_item = get_recurring_item(db, recurring_id, user_id)
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False

# Analytics
def get_monthly_summary(db: Session, user_id: int, months: int = 12):
    results = []
    today = date.today()
    
    for i in range(months):
        month_date = today - timedelta(days=i*30)
        month_start = month_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        income = db.query(func.sum(models.Expense.amount)).filter(
            models.Expense.user_id == user_id,
            models.Expense.is_income == True,
            extract('month', models.Expense.date) == month_date.month,
            extract('year', models.Expense.date) == month_date.year
        ).scalar() or 0
        
        expenses = db.query(func.sum(models.Expense.amount)).filter(
            models.Expense.user_id == user_id,
            models.Expense.is_income == False,
            extract('month', models.Expense.date) == month_date.month,
            extract('year', models.Expense.date) == month_date.year
        ).scalar() or 0
        
        results.append({
            "month": month_date.strftime("%b %Y"),
            "income": float(income),
            "expenses": float(expenses),
            "savings": float(income - expenses)
        })
    
    return list(reversed(results))

def get_category_breakdown(db: Session, user_id: int, start_date: date, end_date: date):
    results = db.query(
        models.Expense.category,
        func.sum(models.Expense.amount).label("total"),
        func.count(models.Expense.id).label("count")
    ).filter(
        models.Expense.user_id == user_id,
        models.Expense.is_income == False,
        models.Expense.date >= start_date,
        models.Expense.date <= end_date
    ).group_by(models.Expense.category).all()
    
    return [{"category": r.category, "total": float(r.total), "count": r.count} for r in results]

def get_budget_status(db: Session, user_id: int):
    budgets = get_budgets(db, user_id)
    today = date.today()
    month_start = today.replace(day=1)
    
    result = []
    for budget in budgets:
        spent = db.query(func.sum(models.Expense.amount)).filter(
            models.Expense.user_id == user_id,
            models.Expense.category == budget.category,
            models.Expense.is_income == False,
            models.Expense.date >= month_start,
            models.Expense.date <= today
        ).scalar() or 0
        
        percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0
        result.append({
            "id": budget.id,
            "category": budget.category,
            "budgeted": budget.amount,
            "spent": float(spent),
            "remaining": budget.amount - float(spent),
            "percentage_used": round(percentage, 1),
            "alert": percentage >= budget.alert_threshold
        })
    
    return result
