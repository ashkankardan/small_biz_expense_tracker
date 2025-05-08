from io import BytesIO
import datetime as dt
from decimal import Decimal
import pytz
from typing import List
import plotly.express as px
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from database import SessionLocal
from models.expense import Expense
from models.category import Category
import plotly.io as pio
import base64

def fetch_expenses(user_id: int, start: dt.datetime, end: dt.datetime, category_id: int | None) -> List[Expense]:
    with SessionLocal() as db:
        q = (
            db.query(Expense)
            .options(joinedload(Expense.category))
            .filter(
                Expense.user_id == user_id,
                Expense.date >= start,
                Expense.date <= end,
            )
        )
        if category_id:
            q = q.filter(Expense.category_id == category_id)
        return q.order_by(Expense.date).all()

def list_categories_for_user(user_id: int):
    with SessionLocal() as db:
        return (
            db.query(Category)
            .filter((Category.user_id == user_id) | (Category.user_id.is_(None)))
            .order_by(Category.name)
            .all()
        )

def build_pdf(expenses, tz_str: str) -> bytes:
    tz = pytz.timezone(tz_str)
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    elems = []

    elems.append(Paragraph("Expense Report", styles["Title"]))
    elems.append(Spacer(1, 12))

    if expenses:
        fig = line_chart_from_expenses(expenses, tz_str)
        if fig:
            img_bytes = pio.to_image(fig, format="png")
            img_buf = BytesIO(img_bytes)
            img = Image(img_buf, width=450, height=300)
            elems.append(img)
            elems.append(Spacer(1, 20))

    data = [["Date", "Amount ($)", "Category", "Description"]]
    for ex in expenses:
        data.append(
            [
                ex.date.astimezone(tz).strftime("%Y-%m-%d"),
                f"{ex.amount:.2f}",
                ex.category.name if ex.category else "",
                ex.description,
            ]
        )
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ]
        )
    )
    elems.append(table)
    doc.build(elems)
    return buf.getvalue()

def line_chart_from_expenses(expenses, tz_str: str):
    tz = pytz.timezone(tz_str)
    if not expenses:
        return None
    df = {
        "Date": [ex.date.astimezone(tz).date() for ex in expenses],
        "Amount": [Decimal(ex.amount) for ex in expenses],
    }
    fig = px.line(df, x="Date", y="Amount", markers=True)
    fig.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(
            tickformat="%Y-%m-%d",
            tickangle=45
        )
    )
    return fig
