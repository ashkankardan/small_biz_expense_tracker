import uuid
import pytest
import bcrypt
import streamlit as st
from services.auth import authenticate_user, _create_session_cookie, destroy_session_cookie
from database import SessionLocal, engine
from models.user import User

HOME_PAGE = "pages/1_Add_New.py"

@pytest.fixture(autouse=True)
def test_db():
    connection = engine.connect()
    trans = connection.begin()

    testing_session = SessionLocal(bind=connection)
    
    original_session_factory = SessionLocal
    
    def get_test_session():
        return testing_session
    
    globals()["SessionLocal"] = get_test_session

    yield testing_session

    globals()["SessionLocal"] = original_session_factory
    
    trans.rollback()
    connection.close()


@pytest.fixture
def test_user(test_db):
    email = "user@example.com"
    pwd_hash = bcrypt.hashpw(b"correct_password", bcrypt.gensalt())
    usr = User(
        id=uuid.uuid4().int & (1 << 31) - 1,
        email=email,
        password_hash=pwd_hash.decode(),
    )
    test_db.add(usr)
    test_db.commit()
    return usr


def test_invalid_email_format():
    success, status = authenticate_user("bad-email-format", "irrelevant")
    assert success is False
    assert status == "invalid_email"


def test_invalid_credentials(test_user):
    success, status = authenticate_user(test_user.email, "wrong_password")
    assert success is False
    assert status == "invalid_credentials"


def test_successful_login_switches_page(monkeypatch, mocker, test_user, test_db):
    called = {"page": None}

    def fake_switch(page):
        called["page"] = page

    monkeypatch.setattr(st, "switch_page", fake_switch, raising=True)
    
    mocker.patch('services.auth._create_session_cookie', return_value=None)
    
    success, status = authenticate_user(test_user.email, "correct_password", db=test_db, redirect=False)
    
    st.switch_page(HOME_PAGE)
    
    assert success is True
    assert status == "success"
    assert called["page"] == HOME_PAGE
