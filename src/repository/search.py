from datetime import date, datetime
from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import Contact, User


async def get_contact_by_firstname(user: User, firstname: str, db: Session) -> List[Contact]:
    contacts = db.query(Contact).filter(
        and_(Contact.user_id == user.id, Contact.firstname.like(f'%{firstname}%'))).all()
    return contacts


async def get_contact_by_lastname(user: User, lastname: str, db: Session) -> List[Contact]:
    contacts = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.lastname.like(f'%{lastname}%'))).all()
    return contacts


async def get_contact_by_email(user: User, email: str, db: Session) -> List[Contact]:
    contacts = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.email.like(f'%{email}%'))).all()
    return contacts


async def get_contact_by_phone(user: User, phone: str, db: Session) -> List[Contact]:
    contacts = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.phone.like(f'%{phone}%'))).all()
    return contacts


async def get_birthday_list(user: User, shift: int, db: Session) -> List[Contact]:
    contacts = []
    all_contacts = db.query(Contact).filter_by(user_id=user.id).all()
    today = date.today()
    for contact in all_contacts:
        birthday = contact.birthday
        evaluated_date = (datetime(today.year, birthday.month, birthday.day).date() - today).days
        if evaluated_date < 0:
            evaluated_date = (datetime(today.year + 1, birthday.month, birthday.day).date() - today).days
        if evaluated_date <= shift:
            contacts.append(contact)
    return contacts


async def get_users_by_partial_info(user: User, partial_info: str, db: Session) -> List[Contact]:
    contacts = []
    search_by_firstname = await get_contact_by_firstname(user, partial_info, db)
    if search_by_firstname:
        for item in search_by_firstname:
            contacts.append(item)
    search_by_second_name = await get_contact_by_lastname(user, partial_info, db)
    if search_by_second_name:
        for item in search_by_second_name:
            contacts.append(item)
    search_by_email = await get_contact_by_email(user, partial_info, db)
    if search_by_email:
        for item in search_by_email:
            contacts.append(item)
    search_by_phone = await get_contact_by_phone(user, partial_info, db)
    if search_by_phone:
        for item in search_by_phone:
            contacts.append(item)
    return contacts