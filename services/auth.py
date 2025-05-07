import streamlit as st
import uuid
import datetime as dt
import re
from database import SessionLocal
from models.session_token import SessionToken
import bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from models.user import User
from database import SessionLocal
from services.cookies import cookies

COOKIE_NAME = "sbet_auth"

# ---------- password helpers ----------
def hash_password(raw_password: str) -> bytes:
    return bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt())

def verify_password(raw_password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(raw_password.encode(), hashed)

# ---------- persistent cookie helpers ----------
def _to_utc_aware(d: dt.datetime) -> dt.datetime:
    if d.tzinfo is None:
        return d.replace(tzinfo=dt.timezone.utc)
    return d.astimezone(dt.timezone.utc)

def _create_session_cookie(user_id: int):
    token = str(uuid.uuid4())
    expires_at = _to_utc_aware(dt.datetime.now(dt.UTC) + dt.timedelta(days=30))

    with SessionLocal() as db:
        db.add(SessionToken(token=token, user_id=user_id, expires_at=expires_at))
        db.commit()

    cookies[COOKIE_NAME] = {"value": token, "max_age": 30 * 24 * 60 * 60}
    cookies.save()

def destroy_session_cookie():
    cookies[COOKIE_NAME] = {"value": "", "max_age": 0}
    cookies.save()

def check_persistent_login():
    raw_cookie = cookies.get(COOKIE_NAME)
    if not raw_cookie:
        return None

    token = raw_cookie["value"] if isinstance(raw_cookie, dict) else raw_cookie
    
    now_utc = dt.datetime.now(dt.UTC)
    now_utc = _to_utc_aware(dt.datetime.now(dt.UTC))

    with SessionLocal() as db:
        record = db.query(SessionToken).filter_by(token=token).first()
        if record and _to_utc_aware(record.expires_at) > now_utc:
            return record.user_id
    return None

# ---------- public API ----------
def register_user(email: str, raw_password: str) -> tuple[bool, str]:
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "invalid_email"

    with SessionLocal() as db:
        user = User(email=email,
                    password_hash=hash_password(raw_password),
                    created_at=dt.datetime.now(dt.UTC))
        db.add(user)
        try:
            db.commit()
            return True, "success"
        except IntegrityError:
            db.rollback()
            return False, "email_exists"

def authenticate_user(email: str, raw_password: str) -> bool:
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email).first()
        if user and verify_password(raw_password, user.password_hash):
            _create_session_cookie(user.id)
            return True
        return False