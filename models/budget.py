from datetime import datetime, date, timedelta
from sqlalchemy import Integer, String, Numeric, ForeignKey, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from sqlalchemy.ext.declarative import declared_attr
from .base import Base
from .expense import Expense

class Budget(Base):
    __tablename__ = "budgets"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    type: Mapped[str] = mapped_column(String(50))
    
    __mapper_args__ = {
        "polymorphic_identity": "budget",
        "polymorphic_on": "type",
    }
    
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")
    
    def period_start(self) -> date:
        raise NotImplementedError
        
    def period_end(self) -> date:
        raise NotImplementedError
    
    def remaining(self, session: Session) -> float:
        expenses_sum = session.execute(
            select(func.sum(Expense.amount))
            .where(
                Expense.user_id == self.user_id,
                Expense.date.between(self.period_start(), self.period_end()),
                Expense.category_id == self.category_id if self.category_id else True
            )
        ).scalar() or 0.0
        
        return float(self.amount) - float(expenses_sum)

class DailyBudget(Budget):
    __tablename__ = "daily_budgets"
    
    id: Mapped[int] = mapped_column(Integer, ForeignKey("budgets.id"), primary_key=True)
    
    __mapper_args__ = {
        "polymorphic_identity": "daily"
    }
    
    def period_start(self) -> date:
        return date.today()
        
    def period_end(self) -> date:
        return date.today()

class WeeklyBudget(Budget):
    __tablename__ = "weekly_budgets"
    
    id: Mapped[int] = mapped_column(Integer, ForeignKey("budgets.id"), primary_key=True)
    
    __mapper_args__ = {
        "polymorphic_identity": "weekly"
    }
    
    def period_start(self) -> date:
        today = date.today()
        return today - timedelta(days=today.isoweekday() - 1)
        
    def period_end(self) -> date:
        return self.period_start() + timedelta(days=6)

class MonthlyBudget(Budget):
    __tablename__ = "monthly_budgets"
    
    id: Mapped[int] = mapped_column(Integer, ForeignKey("budgets.id"), primary_key=True)
    
    __mapper_args__ = {
        "polymorphic_identity": "monthly"
    }
    
    def period_start(self) -> date:
        today = date.today()
        return date(today.year, today.month, 1)
        
    def period_end(self) -> date:
        start = self.period_start()
        if start.month == 12:
            next_month = date(start.year + 1, 1, 1)
        else:
            next_month = date(start.year, start.month + 1, 1)
        return next_month - timedelta(days=1) 