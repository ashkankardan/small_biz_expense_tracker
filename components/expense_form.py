import datetime as dt
from datetime import timezone
import streamlit as st
import time
from decimal import Decimal, InvalidOperation
from sqlalchemy.orm import Session
from database import SessionLocal
from models.category import Category
from models.expense import Expense

def _currency_to_decimal(text: str) -> Decimal | None:
    try:
        clean = text.replace("$", "").replace(",", "").strip()
        return Decimal(clean)
    except (InvalidOperation, AttributeError):
        return None

def add_expense_form(user_id: int) -> None:
    st.header("Add New Expense")

    with SessionLocal() as db:
        categories = (
            db.query(Category)
            .filter((Category.user_id == user_id) | (Category.user_id.is_(None)))
            .order_by(Category.name)
            .all()
        )

    if not categories:
        st.warning(
            "You must create at least one category in **Settings** before adding expenses."
        )
        return

    with st.form("expense_form", clear_on_submit=True):
        date     = st.date_input("Date", value=dt.date.today(), format="MM/DD/YYYY")
        amount_t = st.text_input("Amount", placeholder="$0.00")
        cat_dict = {c.name: c.id for c in categories}
        cat_name = st.selectbox("Category", options=list(cat_dict.keys()))
        desc     = st.text_area("Description", placeholder="Description of the expense…")

        submitted = st.form_submit_button("Submit")

    if submitted:
        amount = _currency_to_decimal(amount_t)
        if amount is None or amount <= 0:
            st.error("Enter a valid positive **Amount** in dollars (e.g., 125.50).")
            return

        if not desc.strip():
            st.error("**Description** is required.")
            return

        local_dt = dt.datetime.combine(date, dt.time())
        expense_date = local_dt.astimezone(timezone.utc)

        with SessionLocal() as db:
            db.add(
                Expense(
                    user_id     = user_id,
                    category_id = cat_dict[cat_name],
                    date        = expense_date,
                    amount      = float(amount),
                    description = desc.strip(),
                    created_at  = dt.datetime.now(timezone.utc),
                )
            )
            db.commit()

        st.success("Expense added successfully!")
        time.sleep(1)
        st.rerun()
