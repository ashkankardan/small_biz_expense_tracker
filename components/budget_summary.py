import streamlit as st
from sqlalchemy.orm import Session
from database import SessionLocal
from services.finance import get_budget_summary

def show_budget_summary(user_id: int):
    with SessionLocal() as session:
        summaries = get_budget_summary(session, user_id)

    cols = st.columns(3)
    for col, summary in zip(cols, summaries):
        with col:
            spent_str  = f"${summary.spent:,.2f}"
            budget_str = f"${summary.budget:,.2f}"
            st.markdown(
                f"""
                <div style="text-align:center;
                            border:1px solid {summary.color};
                            padding:0.75rem;
                            border-radius:4px;
                            color:{summary.color};">
                    <strong>{summary.period_label} Budget:</strong><br>
                    {spent_str} / {budget_str}
                </div>
                """,
                unsafe_allow_html=True,
            )
