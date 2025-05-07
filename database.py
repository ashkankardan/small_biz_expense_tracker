from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import *

DB_PATH = Path(".data/expenses.db")
DB_PATH.parent.mkdir(exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

def seed_defaults():
    from models.category import Category
    with SessionLocal() as session:
        if not session.query(Category).filter(Category.user_id.is_(None)).first():
            default_categories = [
                Category(name=name, user_id=None)
                for name in ["Travel", "Meals", "Software", "Other"]
            ]
            session.add_all(default_categories)
            session.commit()

def init_db() -> None:
    from models import user, category, expense, budget

    Base.metadata.create_all(engine)
    
    seed_defaults()