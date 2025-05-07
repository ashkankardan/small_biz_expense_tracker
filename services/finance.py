import datetime as dt
from collections import namedtuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.expense import Expense
from models.budget import DailyBudget, WeeklyBudget, MonthlyBudget

Summary = namedtuple("Summary", "period_label spent budget color")

def _period_edges(period: str, today: dt.date) -> tuple[dt.datetime, dt.datetime]:
    if period == "daily":
        start = dt.datetime.combine(today, dt.time.min)
        end = dt.datetime.combine(today, dt.time.max)
    elif period == "weekly":
        start_of_week = today - dt.timedelta(days=today.weekday())
        end_of_week   = start_of_week + dt.timedelta(days=6)
        start = dt.datetime.combine(start_of_week, dt.time.min)
        end = dt.datetime.combine(end_of_week,   dt.time.max)
    elif period == "monthly":
        start_of_month = today.replace(day=1)
        next_month = start_of_month.replace(day=28) + dt.timedelta(days=4)
        last_day = next_month - dt.timedelta(days=next_month.day)
        start = dt.datetime.combine(start_of_month, dt.time.min)
        end = dt.datetime.combine(last_day, dt.time.max)
    else:
        raise ValueError(period)
    return start, end

def get_budget_summary(session: Session, user_id: int) -> list[Summary]:
    today = dt.date.today()
    results: list[Summary] = []

    mapping = [
        ("daily", DailyBudget, "Daily"),
        ("weekly", WeeklyBudget, "Weekly"),
        ("monthly", MonthlyBudget, "Monthly"),
    ]

    for key, model, label in mapping:
        start, end = _period_edges(key, today)
        spent = (
            session.query(Expense)
            .filter(Expense.user_id == user_id,
                    Expense.date >= start,
                    Expense.date <= end)
            .with_entities(func.coalesce(func.sum(Expense.amount), 0))
            .scalar() or 0
        )

        budget_obj = (
            session.query(model)
            .filter(model.user_id == user_id, model.category_id == None)
            .first()
        )
        budget_amt = budget_obj.amount if budget_obj else 0

        color = (
            "green"  if spent <  budget_amt else
            "orange" if spent == budget_amt else
            "red"
        )
        results.append(Summary(label, spent, budget_amt, color))
    return results
