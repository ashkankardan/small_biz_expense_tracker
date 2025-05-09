import streamlit as st
import time
from sqlalchemy.orm import Session
from sqlalchemy import exists
from database import SessionLocal
from models.category import Category
from models.expense  import Expense


def _get_categories(session: Session, user_id: int):
    return (
        session.query(Category)
        .filter((Category.user_id == user_id) | (Category.user_id.is_(None)))
        .order_by(Category.name)
        .all()
    )


def _category_in_use(session: Session, cat_id: int) -> bool:
    return session.query(exists().where(Expense.category_id == cat_id)).scalar()


def render_category_settings(user_id: int) -> None:
    st.subheader("Category Settings")

    with SessionLocal() as db:
        cats = _get_categories(db, user_id)

    if not cats:
        st.info("No categories yet. Add one below.")
    else:
        header_cols = st.columns([3, 1])
        header_cols[0].markdown("**Category:**")
        header_cols[1].markdown("**Action**")

        for cat in cats:
            row = st.columns([3, 1])
            row[0].markdown(cat.name)

            delete_key = f"del_{cat.id}"
            if row[1].button("Delete", key=delete_key):
                with SessionLocal() as db:
                    if _category_in_use(db, cat.id):
                        st.warning(
                            f"Cannot delete **{cat.name}** – there are expenses recorded under this category."
                        )
                        time.sleep(3)
                        st.rerun()
                    else:
                        db.query(Category).filter(Category.id == cat.id).delete()
                        db.commit()
                        st.success(f"Category **{cat.name}** deleted.")
                        time.sleep(1)
                        st.rerun()

    st.markdown("---")

    st.markdown("#### Add New Category")
    with st.form("add_cat_form", clear_on_submit=True):
        new_name = st.text_input("New Category Name:")
        submitted = st.form_submit_button("Add Category")

    if submitted:
        new_name = new_name.strip()
        if not new_name:
            st.error("Category name cannot be empty.")
            st.stop()

        with SessionLocal() as db:
            duplicate = (
                db.query(Category)
                .filter(
                    Category.name.ilike(new_name),
                    (Category.user_id == user_id) | (Category.user_id.is_(None)),
                )
                .first()
            )
            if duplicate:
                st.warning(f"A category named **{new_name}** already exists.")
                time.sleep(3)
                st.rerun()
            else:
                db.add(Category(name=new_name, user_id=user_id))
                db.commit()
                st.success(f"Category **{new_name}** added.")
                time.sleep(1)
                st.rerun()
