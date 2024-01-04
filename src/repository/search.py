from datetime import date, datetime
from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import Contact, User


async def get_contact_by_firstname(user: User, firstname: str, db: Session) -> List[Contact]:
    """
    The get_contact_by_firstname function returns a list of contacts that match the firstname parameter.
        The user_id is used to ensure that only contacts belonging to the current user are returned.
    
    :param user: User: Identify the user that is making the request
    :param firstname: str: Search for contacts by firstname
    :param db: Session: Access the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter(
        and_(Contact.user_id == user.id, Contact.firstname.like(f'%{firstname}%'))).all()
    return contacts


async def get_contact_by_lastname(user: User, lastname: str, db: Session) -> List[Contact]:
    """
    The get_contact_by_lastname function returns a list of contacts that match the lastname parameter.
        
    
    :param user: User: Get the user_id from the user object
    :param lastname: str: Filter the contacts by lastname
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.lastname.like(f'%{lastname}%'))).all()
    return contacts


async def get_contact_by_email(user: User, email: str, db: Session) -> List[Contact]:
    """
    The get_contact_by_email function returns a list of contacts that match the email provided.
        
    
    :param user: User: Get the user's id from the database
    :param email: str: Search for a contact by email
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
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
            db (Session): A connection to our database session, used for querying and updating data in our tables.
        Returns: 
            List[Contact]: A list of contacts matching the given criteria.
    
    :param user: User: Get the user's id from the database
    :param phone: str: Filter the contacts by phone number
    :param db: Session: Pass a database session to the function
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.phone.like(f'%{phone}%'))).all()
    return contacts


async def get_birthday_list(user: User, shift: int, db: Session) -> List[Contact]:
    """
    The get_birthday_list function returns a list of contacts whose birthdays are within the next 7 days.
        
    
    :param user: User: Get the user id from the user object
    :param shift: int: Set the range of days in which we want to get birthdays
    :param db: Session: Access the database
    :return: A list of contacts that have a birthday in the next shift days
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


async def get_users_by_partial_info(user: User, partial_info: str, db: Session) -> List[Contact]:
    """
    The get_users_by_partial_info function takes in a user, partial_info, and db.
    It then searches for contacts by firstname, lastname, email or phone number that match the partial_info string.
    If any of these are found it appends them to a list called contacts and returns this list.
    
    :param user: User: Get the user_id of the user
    :param partial_info: str: Search by firstname, lastname, email and phone number
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
    :doc-author: Trelent
    """
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