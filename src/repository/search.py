from datetime import date, datetime
from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import Contact, User


async def get_contact_by_firstname(user: User, firstname: str, db: Session) -> List[Contact]:
    """
    The get_contact_by_firstname function returns a list of contacts that match the firstname parameter.
        The function takes in a user object, firstname string and database session as parameters.

    :param user: User: Get the user id of the logged in user
    :param firstname: str: Search for a contact by firstname
    :param db: Session: Create a database session, which is used to query the database
    :return: A list of contacts that match the firstname given
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter(
        and_(Contact.user_id == user.id, Contact.firstname.like(f'%{firstname}%'))).all()
    return contacts


async def get_contact_by_lastname(user: User, lastname: str, db: Session) -> List[Contact]:
    """
    The get_contact_by_lastname function returns a list of contacts that match the lastname parameter.
        The user_id is used to ensure that only contacts belonging to the current user are returned.

    :param user: User: Get the user's id from the user object
    :param lastname: str: Filter the contacts by lastname
    :param db: Session: Create a database session
    :return: A list of contacts with the given lastname
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.lastname.like(f'%{lastname}%'))).all()
    return contacts


async def get_contact_by_email(user: User, email: str, db: Session) -> List[Contact]:
    """
    The get_contact_by_email function takes in a user, an email string, and a database session.
    It then queries the database for all contacts that match the given email string.
    The function returns a list of contacts.

    :param user: User: Filter the contacts by user id
    :param email: str: Search for a contact by email
    :param db: Session: Pass the database session to the function
    :return: A list of contacts that match the email address
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.email.like(f'%{email}%'))).all()
    return contacts


async def get_contact_by_phone(user: User, phone: str, db: Session) -> List[Contact]:
    """
    The get_contact_by_phone function returns a list of contacts that match the phone number provided.
        Args:
            user (User): The user who is making the request.
            phone (str): The phone number to search for in the database.

    :param user: User: Filter the contacts by user
    :param phone: str: Search for a contact by phone number
    :param db: Session: Pass the database session to the function
    :return: A list of contacts that match the user's id and phone number
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.phone.like(f'%{phone}%'))).all()
    return contacts


async def get_birthday_list(user: User, shift: int, db: Session) -> List[Contact]:
    """
    The get_birthday_list function takes in a user, shift, and db.
    It returns a list of contacts that have birthdays within the next 'shift' days.

    :param user: User: Identify the user that is currently logged in
    :param shift: int: Determine how many days in the future to look for birthdays
    :param db: Session: Access the database
    :return: A list of contacts whose birthdays are within the next 'shift' days
    :doc-author: Trelent
    """
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

#
# async def get_users_by_partial_info(user: User, partial_info: str, db: Session) -> List[Contact]:
#     """
#     The get_users_by_partial_info function takes in a user and partial_info,
#         then returns a list of contacts that match the partial_info.
#
#     :param user: User: Identify the user who is making the request
#     :param partial_info: str: Search for a user by their first name, last name, email or phone number
#     :param db: Session: Pass the database session to the function
#     :return: A list of contacts
#     :doc-author: Trelent
#     """
#     contacts = []
#     search_by_firstname = await get_contact_by_firstname(user, partial_info, db)
#     if search_by_firstname:
#         for item in search_by_firstname:
#             contacts.append(item)
#     search_by_second_name = await get_contact_by_lastname(user, partial_info, db)
#     if search_by_second_name:
#         for item in search_by_second_name:
#             contacts.append(item)
#     search_by_email = await get_contact_by_email(user, partial_info, db)
#     if search_by_email:
#         for item in search_by_email:
#             contacts.append(item)
#     search_by_phone = await get_contact_by_phone(user, partial_info, db)
#     if search_by_phone:
#         for item in search_by_phone:
#             contacts.append(item)
#     return contacts

async def get_users_by_partial_info(user: User, partial_info: str, db: Session) -> List[Contact]:
    contacts = db.query(Contact).filter(Contact.user_id == user.id).all()
    filtered_contacts = [contact for contact in contacts if
                         partial_info in contact.firstname or
                         partial_info in contact.lastname or
                         partial_info in contact.email or
                         partial_info in contact.phone]
    return filtered_contacts