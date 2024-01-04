import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.repository.contacts import (
    get_contacts, get_contact_by_id, create, update, remove, set_favorite
)
from src.schemas import ContactModel, ContactFavoriteModel


class TestContacts(IsolatedAsyncioTestCase):
   def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
