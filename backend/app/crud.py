from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date
from . import models, schemas

def create_expense(db: Session, expense: schemas.ExpenseCreate, user_id: int):
    db_expense = models.Expense(**expense.dict(), user_id=user_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expenses(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Expense).filter(models.Expense.user_id == user_id)\
        .order_by(models.Expense.date.desc()).offset(skip).limit(limit).all()

def get_expense(db: Session, expense_id: int, user_id: int):
    return db.query(models.Expense).filter(models.Expense.id == expense_id, models.Expense.user_id == user_id).first()

def delete_expense(db: Session, expense_id: int, user_id: int):
    db_expense = get_expense(db, expense_id, user_id)
    if db_expense:
        db.delete(db_expense)
        db.commit()
        return True
    return False

def create_budget(db: Session, budget: schemas.BudgetCreate, user_id: int):
    db_budget = models.Budget(**budget.dict(), user_id=user_id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def get_budgets(db: Session, user_id: int):
    return db.query(models.Budget).filter(models.Budget.user_id == user_id, models.Budget.is_active == True).all()

def delete_budget(db: Session, budget_id: int, user_id: int):
    db_budget = db.query(models.Budget).filter(models.Budget.id == budget_id, models.Budget.user_id == user_id).first()
    if db_budget:
        db.delete(db_budget)
        db.commit()
        return True
    return False

def create_goal(db: Session, goal: schemas.GoalCreate, user_id: int):
    db_goal = models.Goal(**goal.dict(), user_id=user_id)
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

def get_goals(db: Session, user_id: int):
    return db.query(models.Goal).filter(models.Goal.user_id == user_id, models.Goal.is_active == True).all()

def delete_goal(db: Session, goal_id: int, user_id: int):
    db_goal = db.query(models.Goal).filter(models.Goal.id == goal_id, models.Goal.user_id == user_id).first()
    if db_goal:
        db.delete(db_goal)
        db.commit()
        return True
    return False

def create_recurring(db: Session, recurring: schemas.RecurringCreate, user_id: int):
    db_recurring = models.RecurringExpense(**recurring.dict(), user_id=user_id)
    db.add(db_recurring)
    db.commit()
    db.refresh(db_recurring)
    return db_recurring

def get_recurring(db: Session, user_id: int):
    return db.query(models.RecurringExpense).filter(models.RecurringExpense.user_id == user_id, models.RecurringExpense.is_active == True).order_by(models.RecurringExpense.next_due_date).all()

def delete_recurring(db: Session, recurring_id: int, user_id: int):
    db_item = db.query(models.RecurringExpense).filter(models.RecurringExpense.id == recurring_id, models.RecurringExpense.user_id == user_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False

def get_monthly_summary(db: Session, user_id: int, months: int = 6):
    from datetime import timedelta
    results = []
    today = date.today()
    for i in range(months):
        month_date = today - timedelta(days=i*30)
        income = db.query(func.sum(models.Expense.amount)).filter(
            models.Expense.user_id == user_id, models.Expense.is_income == True,
            extract('month', models.Expense.date) == month_date.month,
            extract('year', models.Expense.date) == month_date.year
        ).scalar() or 0
        expenses = db.query(func.sum(models.Expense.amount)).filter(
            models.Expense.user_id == user_id, models.Expense.is_income == False,
            extract('month', models.Expense.date) == month_date.month,
            extract('year', models.Expense.date) == month_date.year
        ).scalar() or 0
        results.append({"month": month_date.strftime("%b %Y"), "income": float(income), "expenses": float(expenses), "savings": float(income - expenses)})
    return list(reversed(results))

def get_budget_status(db: Session, user_id: int):
    budgets = get_budgets(db, user_id)
    today = date.today()
    month_start = today.replace(day=1)
    result = []
    for budget in budgets:
        spent = db.query(func.sum(models.Expense.amount)).filter(
            models.Expense.user_id == user_id, models.Expense.category == budget.category,
            models.Expense.is_income == False, models.Expense.date >= month_start
        ).scalar() or 0
        percentage = (spent / budget.amount * 100) if budget.amount > 0 else 0
        result.append({
            "id": budget.id, "category": budget.category, "budgeted": budget.amount,
            "spent": float(spent), "remaining": budget.amount - float(spent),
            "percentage_used": round(percentage, 1), "alert": percentage >= budget.alert_threshold
        })
    return result
