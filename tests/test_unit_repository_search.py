import unittest
from datetime import datetime
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import User, Contact
from src.repository.search import (
    get_contact_by_firstname,
    get_contact_by_lastname,
    get_contact_by_email,
    get_contact_by_phone,
    get_birthday_list,
    get_users_by_partial_info)
from src.schemas import ContactModel


class TestSearch(IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.contacts = [Contact(id=i, firstname=f"firstname{i}",
                                 lastname=f"lastname{i}",
                                 email=f"email{i}@example.com",
                                 phone=f"380{i}01234567",
                                 birthday=datetime.strptime("2023-05-04", "%Y-%m-%d"),
                                 ) for i in range(9)]

    def tearDown(self):
        self.session.delete()
        self.user = None
        self.contacts = None

    async def test_get_contact_by_firstname(self):
        self.session.query().filter().all.return_value = self.contacts
        result = await get_contact_by_firstname(self.user, "firstname2", self.session)
        self.assertEqual(result, self.contacts)
        self.session.query().filter().all.assert_called_once()

    async def test_get_contact_by_lastname(self):
        self.session.query().filter().all.return_value = self.contacts
        result = await get_contact_by_lastname(self.user, "lastname2", self.session)
        self.assertEqual(result, self.contacts)
        self.session.query().filter().all.assert_called_once()

    async def test_get_contact_by_email(self):
        self.session.query().filter().all.return_value = self.contacts
        result = await get_contact_by_email(self.user, "email2@@example.com", self.session)
        self.assertEqual(result, self.contacts)
        self.session.query().filter().all.assert_called_once()

    async def test_get_contact_by_phone(self):
        self.session.query().filter().all.return_value = self.contacts
        result = await get_contact_by_phone(self.user, "380501234567", self.session)
        self.assertEqual(result, self.contacts)
        self.session.query().filter().all.assert_called_once()

    async def test_get_birthday_list(self):
        self.session.query(Contact).filter_by(user_id=self.user.id).all.return_value = self.contacts
        # self.session.query().filter().all.return_value = self.contacts
        result = await get_birthday_list(self.user, 360, self.session)
        self.assertListEqual(result, self.contacts)

    async def test_get_users_by_partial_info(self):
        self.session.query().filter().all.return_value = self.contacts
        result = await get_users_by_partial_info(self.user, "firstname1", self.session)
        self.assertEqual(result[0], self.contacts[1])
        self.assertNotEqual(result[0], self.contacts[3])

if __name__ == '__main__':
    unittest.main()