from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, ForeignKey
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String(255))
    category = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    is_income = Column(Boolean, default=False)
    payment_method = Column(String(50), default="cash")
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    alert_threshold = Column(Float, default=80.0)
    start_date = Column(Date, nullable=False)
    period = Column(String, default="monthly")
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"))

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    deadline = Column(Date)
    category = Column(String, default="savings")
    color = Column(String, default="#3b82f6")
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"))

class RecurringExpense(Base):
    __tablename__ = "recurring_expenses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    next_due_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"))
