from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class ExpenseCategory(str, enum.Enum):
    FOOD = "Food & Dining"
    TRANSPORT = "Transportation"
    HOUSING = "Housing & Utilities"
    ENTERTAINMENT = "Entertainment"
    SHOPPING = "Shopping"
    HEALTH = "Health & Fitness"
    TRAVEL = "Travel"
    EDUCATION = "Education"
    SUBSCRIPTIONS = "Subscriptions"
    INCOME = "Income"
    OTHER = "Other"

class RecurringFrequency(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    currency = Column(String, default="USD")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    expenses = relationship("Expense", back_populates="owner")
    budgets = relationship("Budget", back_populates="owner")
    goals = relationship("Goal", back_populates="owner")
    recurring = relationship("RecurringExpense", back_populates="owner")

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String(255))
    category = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    is_income = Column(Boolean, default=False)
    payment_method = Column(String(50), default="cash")
    tags = Column(Text)  # JSON string
    receipt_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="expenses")

class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    period = Column(String, default="monthly")  # monthly, weekly
    alert_threshold = Column(Float, default=80.0)  # percentage
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="budgets")

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
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="goals")

class RecurringExpense(Base):
    __tablename__ = "recurring_expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    next_due_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    auto_pay = Column(Boolean, default=False)
    payment_method = Column(String(50))
    
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="recurring")
