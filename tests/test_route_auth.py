import asyncio
import unittest
from unittest.mock import MagicMock

import pytest

from src.services.auth import auth_service
from src.conf import messages

from src.database.models import User


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == user.get("email")
    assert "id" in data


def test_repeat_create_user(client, user):
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == messages.ACCOUNT_EXIST


def test_login_ok(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()

    response = client.post("api/auth/login", data={"username": user.get("email"), "password": user.get("password")})
    data = response.json()

    assert response.status_code == 200, response.text
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()

    response = client.post("api/auth/login", data={"username": user.get("email"), "password": "fake_password"})
    data = response.json()

    assert response.status_code == 401, response.text
    assert data["detail"] == messages.INVALID_PASSWORD


def test_login_user_not_exist(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = False
    session.commit()

    response = client.post("api/auth/login", data={"username": "fake@mail.com", "password": user.get("password")})
    data = response.json()

    assert response.status_code == 401, response.text
    assert data["detail"] == messages.INVALID_EMAIL


def test_login_user_not_confirmed(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = False
    session.commit()

    response = client.post("api/auth/login", data={"username": user.get("email"), "password": user.get("password")})
    data = response.json()

    assert response.status_code == 401, response.text
    assert data["detail"] == messages.EMAIL_NOT_CONFIRMED


def test_refresh_token_ok(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()

    headers = {"Authorization": f"Bearer {current_user.refresh_token}"}
    response = client.get("api/auth/refresh_token", headers=headers)

    assert response.status_code == 200, response.text
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"] is not None
    assert response.json()["refresh_token"] is not None


def test_refresh_token_fail(client, user):
    headers = {"Authorization": f"Bearer fake token"}
    response = client.get("api/auth/refresh_token", headers=headers)

    assert response.status_code == 401, response.text
    assert response.json()["detail"] == messages.INVALID_REFRESH_TOKEN

    fake_refresh_token = asyncio.run(
        auth_service.create_refresh_token(data={"sub": user["email"]}, expires_delta=10)
    )
    headers = {"Authorization": f"Bearer {fake_refresh_token}"}
    response = client.get("api/auth/refresh_token", headers=headers)

    assert response.status_code == 401, response.text
    assert response.json()["detail"] == messages.INVALID_REFRESH_TOKEN


def test_confirmed_email_ok(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = False
    session.commit()

    email_token = auth_service.create_email_token(
        data={
            "sub": user["email"],
            "email": user["email"],
            "username": user["username"],
        }
    )
    response = client.get(f"api/auth/confirmed_email/{email_token}")

    assert response.status_code == 200, response.json()
    assert response.json()["message"] == messages.EMAIL_CONFIRMED


def test_confirmed_email_fail(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()

    email_token = auth_service.create_email_token(
        data={
            "sub": user["email"],
            "email": user["email"],
            "username": user["username"],
        }
    )
    response = client.get(f"api/auth/confirmed_email/{email_token}")

    assert response.status_code == 200, response.json()
    assert response.json()["message"] == messages.EMAIL_ALREADY_CONFIRMED

    email_token = auth_service.create_email_token(data={"sub": "UNKNOWN!@com.com", "email": "-", "username": "-"})
    response = client.get(f"api/auth/confirmed_email/{email_token}")

    assert response.status_code == 400, response.json()
    assert response.json()["detail"] == messages.VERIFICATION_ERROR


def test_request_email_ok(client, session, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()

    response = client.post("api/auth/request_email", json={"email": user.get("email")})

    assert response.status_code == 200, response.json()
    assert response.json()["message"] == messages.EMAIL_ALREADY_CONFIRMED


def test_request_email_check(client, session, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr('src.routes.auth.send_email', mock_send_email)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = False
    session.commit()

    response = client.post("api/auth/request_email", json={"email": user.get("email")})

    assert response.status_code == 200, response.json()
    assert response.json()["message"] == messages.CHECK_EMAIL

    response2 = client.post("api/auth/request_email", json={"email": "Email@notSignUp.user"})

    assert response2.status_code == 200, response2.json()
    assert response2.json()["message"] == messages.CHECK_EMAIL


def test_reset_password_ok(client, session, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()

    response = client.post("api/auth/reset_password", json={"email": user.get("email")})

    assert response.status_code == 200, response.json()
    assert response.json()["message"] == messages.CHECK_EMAIL_NEXT_STEP


def test_reset_password_check1(client, session, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    response = client.post("api/auth/reset_password", json={"email": user.get("email")})

    assert response.status_code == 200, response.json()
    assert response.json()["message"] == messages.CHECK_EMAIL_NEXT_STEP


def test_reset_password_check2(client, session, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    response = client.post("api/auth/reset_password", json={"email": "fake@email.com"})

    assert response.status_code == 200, response.json()
    assert response.json()["message"] == messages.INVALID_EMAIL


def test_password_reset_confirm(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    reset_token = auth_service.create_email_token(data={"sub": current_user.email})
    current_user.password_reset_token = reset_token
    session.commit()

    response = client.get(f"api/auth/password_reset_confirm/{reset_token}")
    current_user.password_reset_token = response.json()["reset_password_token"]
    session.commit()

    assert response.status_code == 200, response.text


def test_update_password_ok(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    reset_token = current_user.password_reset_token

    payload = {"reset_password_token": reset_token, "new_password": "fake_password", "confirm_password": "fake_password"}

    response = client.post("api/auth/set_new_password", json=payload)

    assert response.status_code == 200, response.text
    assert response.json()["message"] == messages.PASSWORD_UPDATED


if __name__ == '__main__':
    unittest.main()