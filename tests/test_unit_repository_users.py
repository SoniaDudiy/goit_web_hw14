import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import User
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar,
    update_password,
    update_reset_token
)
from src.schemas import UserModel


class TestUser(IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.body = UserModel(username="username", email="username@test.ua", password="12345678")
        self.user = User(username="username", email="username@test.ua", password="12345678", refresh_token="token", confirmed=False)

    async def test_get_user_by_email(self):
        email = self.user.email
        db = self.session
        db.query(User).filter_by(email=email).first.return_value = self.user
        result = await get_user_by_email(email, db)
        self.assertEqual(result, self.user)
        self.assertTrue(hasattr(result, "id"))
        self.assertTrue(hasattr(result, "avatar"))
        self.assertTrue(hasattr(result, "roles"))
        self.assertTrue(hasattr(result, "confirmed"))
        self.assertTrue(hasattr(result, "created_at"))
        self.assertTrue(hasattr(result, "updated_at"))

    async def test_create_user(self):
        body = self.body
        db = self.session
        result = await create_user(body, db)
        self.assertEqual(result.username, self.user.username)
        self.assertEqual(result.email, self.user.email)
        self.assertEqual(result.password, self.user.password)
        self.assertTrue(hasattr(result, "id"))
        self.assertTrue(hasattr(result, "avatar"))
        self.assertTrue(hasattr(result, "roles"))
        self.assertTrue(hasattr(result, "confirmed"))
        self.assertTrue(hasattr(result, "refresh_token"))
        self.assertTrue(hasattr(result, "password_reset_token"))
        self.assertTrue(hasattr(result, "updated_at"))

    async def test_update_token(self):
        user = self.user
        db = self.session
        token = user.refresh_token
        result = await update_token(user, token, db)
        self.assertEqual(result.refresh_token, token)

    async def test_confirmed_email(self):
        email = self.user.email
        db = self.session
        db.query(User).filter_by(email=email).first.return_value = self.user
        result = await confirmed_email(email, db)
        self.assertTrue(result.confirmed)

    async def test_update_avatar(self):
        url = "some string"
        user = self.user
        result = await update_avatar(email=self.user.email, url=url, db=self.session)
        self.assertEqual(result.avatar, url)

    async def test_update_password(self):
        user = self.user
        password = "user.password"
        result = await update_password(user, password, self.session)
        self.assertEqual(result.password, password)

    async def test_update_reset_token(self):
        user = self.user
        db = self.session
        token = "some string"
        result = await update_reset_token(user, token, db)
        self.assertEqual(result.password_reset_token, token)


if __name__ == '__main__':
    unittest.main()