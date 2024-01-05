from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from fastapi_limiter.depends import RateLimiter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.database.models import Base, User
from src.database.db import get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session):
    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    """
    The user function returns a dictionary with the following keys:
        username, email, password.


    :return: A dictionary with the user details
    :doc-author: Trelent
    """
    return {
        "username": "Unknown",
        "email": "unknown@example.com",
        "password": "password",
        "refresh_token": None,
        "avatar": "some url",
        "roles": "admin",
        "confirmed": False,
        "password_reset_token": "some string"

    }


@pytest.fixture(scope="function")
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


@pytest.fixture(scope="module")
def contact():
    return {
        "firstname": "Unknown",
        "lastname": "Unknown",
        "email": "unknown@example.com",
        "phone": "1234567890",
        "birthday": "2023-04-04",
        "is_favorite": False,
        "user_id": 1
    }