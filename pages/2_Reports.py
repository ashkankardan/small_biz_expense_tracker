import streamlit as st
import datetime as dt
from services.router import guard_page
from components.sidebar import render as sidebar
from components.budget_summary import show_budget_summary
import os
import pytz
from components.timezone import get_browser_tz
from components.report_utils import (
    fetch_expenses,
    list_categories_for_user,
    line_chart_from_expenses,
    build_pdf,
)

guard_page("pages/Reports.py")

if not st.session_state.logged_in:
    st.stop()

def load_css(css_file):
    with open(css_file, 'r') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'styles.css')
load_css(css_path)


sidebar()
show_budget_summary(st.session_state.user_id)
st.markdown("---")

tz_str = get_browser_tz()
tz = pytz.timezone(tz_str)

st.header("Expense Report")

cols = st.columns([1, 1, 1])
with cols[0]:
    start_date = st.date_input("Start Date:", value=dt.date.today())
with cols[1]:
    end_date = st.date_input("End Date:", value=dt.date.today())
with cols[2]:
    cats = list_categories_for_user(st.session_state.user_id)
    cat_names = ["All Categories"] + [c.name for c in cats]
    sel_name = st.selectbox("Category:", cat_names)
    sel_cat_id = None if sel_name == "All Categories" else next(c.id for c in cats if c.name == sel_name)

btn_col1, btn_col2 = st.columns([1, 1])
generate = btn_col1.button("Generate", use_container_width=True)

if "report_expenses" not in st.session_state:
    start_dt = tz.localize(dt.datetime.combine(dt.date.today(), dt.time.min)).astimezone(pytz.UTC)
    end_dt = tz.localize(dt.datetime.combine(dt.date.today(), dt.time.max)).astimezone(pytz.UTC)
    st.session_state.report_expenses = fetch_expenses(
        st.session_state.user_id, start_dt, end_dt, None
    )

if generate:
    start_dt = tz.localize(dt.datetime.combine(start_date, dt.time.min)).astimezone(pytz.UTC)
    end_dt = tz.localize(dt.datetime.combine(end_date, dt.time.max)).astimezone(pytz.UTC)
    st.session_state.report_expenses = fetch_expenses(
        st.session_state.user_id, start_dt, end_dt, sel_cat_id
    )

if st.session_state.report_expenses:
    pdf_bytes = build_pdf(st.session_state.report_expenses, tz_str)
    btn_col2.download_button(
        label="Download",
        data=pdf_bytes,
        file_name="expense_report.pdf",
        mime="application/pdf",
        use_container_width=True
    )

fig = line_chart_from_expenses(st.session_state.report_expenses, tz_str)
if fig:
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No expenses recorded for the selected period.")

if st.session_state.report_expenses:
    tz = pytz.timezone(tz_str)
    table_data = [
        {
            "Date": ex.date.astimezone(tz).strftime("%Y-%m-%d"),
            "Amount ($)": f"{ex.amount:.2f}",
            "Category": ex.category.name if ex.category else "",
            "Description": ex.description,
        }
        for ex in st.session_state.report_expenses
    ]
    st.dataframe(table_data, use_container_width=True, height=300)
else:
    st.info("No expenses recorded for the selected period.")