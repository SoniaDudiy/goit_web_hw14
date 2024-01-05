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
        self.contacts = [Contact(id=i, firstname=f"firstname{i}", lastname=f"lastname{i}") for i in range(10)]
        self.body = ContactModel(firstname="firstname",
                                 lastname="lastname",
                                 email="email@example.com",
                                 phone="1234567890",
                                 birthday="2021-01-01",
                                 is_favorite=True)
        self.favorite_body = ContactFavoriteModel(firstname="firstname",
                                 lastname="lastname",
                                 email="email@example.com",
                                 phone="1234567890",
                                 birthday="2021-01-01",
                                 is_favorite=True)

   def tearDown(self):
        self.session.delete()
        self.user = None
        self.contacts = None
        self.body = None
    
   async def test_get_contacts(self):
       user = self.user
       limit = 10
       offset = 0
       self.session.query().filter().limit().offset().all.return_value = self.contacts
       result = await get_contacts(user, limit, offset, self.session)
       self.assertEqual(result, self.contacts)

   async def test_get_contact_by_id(self):   
       user = self.user
       contact_id = 1
       contact = Contact(id=contact_id, firstname="firstname", lastname="lastname", user_id=user.id)
       db = self.session
       db.query(Contact).filter(
           and_(Contact.user_id == user.id, Contact.id == contact_id)).first.return_value = contact
       result = await get_contact_by_id(user, contact_id, db)
       self.assertEqual(result, contact)

   async def test_create_contact(self):
       user = self.user
       body = self.body
       db = self.session

       result = await create(user, body, db)
       self.assertEqual(result.firstname, body.firstname)
       self.assertEqual(result.lastname, body.lastname)
       self.assertEqual(result.email, body.email)
       self.assertEqual(result.phone, body.phone)
       self.assertEqual(result.birthday, body.birthday)
       self.assertEqual(result.is_favorite, body.is_favorite)
       self.assertTrue(hasattr(result, "id"))
       self.assertTrue(hasattr(result, "user_id"))
       self.assertTrue(hasattr(result, "created_at"))
       self.assertTrue(hasattr(result, "updated_at"))   

   async def test_update(self):
       user = self.user
       contact_id = 1
       body = self.body
       db = self.session
       contact = Contact(id=contact_id, firstname="old_firstname", lastname="old_lastname",
                          email="old_email@example.com", user_id=user.id)
       db.query(Contact).filter(
            and_(Contact.user_id == user.id, Contact.id == contact_id)).first.return_value = contact
       result = await update(user, contact_id, body, db)
       self.assertEqual(result.firstname, body.firstname)
       self.assertEqual(result.lastname, body.lastname)
       self.assertEqual(result.email, body.email)
       self.assertEqual(result.phone, body.phone)
       self.assertEqual(result.birthday, body.birthday)
       self.assertEqual(result.is_favorite, body.is_favorite)
       self.assertTrue(hasattr(result, "id"))
       self.assertTrue(hasattr(result, "user_id"))
       self.assertTrue(hasattr(result, "created_at"))
       self.assertTrue(hasattr(result, "updated_at"))   

   async def test_remove(self):
       user = self.user
       contact_id = 1
       db = self.session
       contact = Contact(id=contact_id, user_id=user.id)
       db.query(Contact).filter(
            and_(Contact.user_id == user.id, Contact.id == contact_id)).first.return_value = contact
       result = await remove(user, contact_id, db)
       self.assertEqual(result, contact) 

   async def test_set_favorite(self):
       user = self.user
       contact_id = 1
       db = self.session
       contact = Contact(id=contact_id, user_id=user.id, is_favorite=False)
       db.query(Contact).filter(
           and_(Contact.user_id == user.id, Contact.id == contact_id)).first.return_value = contact
       result = await set_favorite(user, contact_id, self.favorite_body, db)
       self.assertEqual(result, contact)
       self.assertTrue(result.is_favorite)   

if __name__ == '__main__':
    unittest.main()       
    
