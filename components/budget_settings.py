import streamlit as st
import time
from sqlalchemy.orm import Session
from database import SessionLocal
from models.budget import DailyBudget, WeeklyBudget, MonthlyBudget

CONVERSION = {
    "daily_to_weekly": lambda d: round(d * 7, 2),
    "daily_to_monthly": lambda d: round(d * 30, 2),
    "weekly_to_daily": lambda w: round(w / 7, 2),
    "weekly_to_monthly": lambda w: round(w * 30 / 7, 2),
    "monthly_to_daily": lambda m: round(m / 30, 2),
    "monthly_to_weekly": lambda m: round(m * 7 / 30, 2),
}

def _load_existing(user_id: int) -> tuple[float, float, float]:
    with SessionLocal() as db:
        daily   = db.query(DailyBudget)   .filter_by(user_id=user_id).first()
        weekly  = db.query(WeeklyBudget)  .filter_by(user_id=user_id).first()
        monthly = db.query(MonthlyBudget) .filter_by(user_id=user_id).first()
        return (
            daily.amount   if daily   else 0.0,
            weekly.amount  if weekly  else 0.0,
            monthly.amount if monthly else 0.0,
        )

def _save_all(user_id: int, d: float, w: float, m: float):
    with SessionLocal() as db:
        def upsert(model, amount):
            obj = db.query(model).filter_by(user_id=user_id).first()
            if obj:
                obj.amount = amount
            else:
                db.add(model(user_id=user_id, amount=amount))

        upsert(DailyBudget,   d)
        upsert(WeeklyBudget,  w)
        upsert(MonthlyBudget, m)
        db.commit()


def render_budget_settings(user_id: int):
    st.subheader("Budget Settings")

    if "budget_loaded" not in st.session_state:
        d, w, m = _load_existing(user_id)
        st.session_state.daily_budget    = d
        st.session_state.weekly_budget   = w or CONVERSION["daily_to_weekly"](d)
        st.session_state.monthly_budget  = m or CONVERSION["daily_to_monthly"](d)
        st.session_state.budget_loaded   = True

    def update_from_daily():
        d = st.session_state.daily_budget
        st.session_state.weekly_budget  = CONVERSION["daily_to_weekly"](d)
        st.session_state.monthly_budget = CONVERSION["daily_to_monthly"](d)

    def update_from_weekly():
        w = st.session_state.weekly_budget
        st.session_state.daily_budget   = CONVERSION["weekly_to_daily"](w)
        st.session_state.monthly_budget = CONVERSION["weekly_to_monthly"](w)

    def update_from_monthly():
        m = st.session_state.monthly_budget
        st.session_state.daily_budget  = CONVERSION["monthly_to_daily"](m)
        st.session_state.weekly_budget = CONVERSION["monthly_to_weekly"](m)

    cols = st.columns(3)
    with cols[0]:
        st.number_input(
            "Daily Budget ($):",
            min_value=0.0,
            step=1.0,
            format="%.2f",
            key="daily_budget",
            on_change=update_from_daily,
        )
    with cols[1]:
        st.number_input(
            "Weekly Budget ($):",
            min_value=0.0,
            step=1.0,
            format="%.2f",
            key="weekly_budget",
            on_change=update_from_weekly,
        )
    with cols[2]:
        st.number_input(
            "Monthly Budget ($):",
            min_value=0.0,
            step=1.0,
            format="%.2f",
            key="monthly_budget",
            on_change=update_from_monthly,
        )

    st.markdown("")

    if st.button("Set Budget", use_container_width=True):
        _save_all(
            user_id,
            st.session_state.daily_budget,
            st.session_state.weekly_budget,
            st.session_state.monthly_budget,
        )
        st.success("Budgets updated successfully!")
        time.sleep(1)
        st.rerun()
