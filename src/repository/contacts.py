from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactFavoriteModel


async def get_contacts(user: User, limit: int, offset: int, db: Session):
    """
    The get_contacts function returns a list of contacts for the user.
        
    
    :param user: User: Get the contacts of a specific user
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Skip the first n contacts
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter(Contact.user_id == user.id).limit(limit).offset(offset).all()
    return contacts


async def get_contact_by_id(user: User, contact_id: int, db: Session):
    """
    The get_contact_by_id function returns a contact object from the database based on the user_id and contact_id.
        Args:
            user (User): The User object that is requesting to get a Contact by id.
            contact_id (int): The id of the Contact being requested.
            db (Session): A Session instance for interacting with our database.
    
    :param user: User: Get the user id from the database
    :param contact_id: int: Specify the id of the contact that we want to get
    :param db: Session: Access the database
    :return: A contact object
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter(and_(Contact.user_id == user.id, Contact.id == contact_id)).first()
    return contact


async def create(user: User, body: ContactModel, db: Session):
    """
    The create function creates a new contact in the database.
        
    
    :param user: User: Get the user id from the token
    :param body: ContactModel: Get the data from the request body
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact = Contact(**body.dict(), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update(user: User, contact_id: int, body: ContactModel, db: Session):
    """
    The update function updates a contact in the database.
        
    
    :param user: User: Get the user_id from the user object
    :param contact_id: int: Identify the contact to be updated
    :param body: ContactModel: Pass in the data from the request body
    :param db: Session: Access the database
    :return: A contact
    :doc-author: Trelent
    """
    contact = await get_contact_by_id(user, contact_id, db)
    if contact:
        contact.firstname = body.firstname
        contact.lastname = body.lastname
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.is_favorite = body.is_favorite
        db.commit()
    return contact


async def remove(user: User, contact_id: int, db: Session):
    """
    The remove function removes a contact from the database.
        
    
    :param user: User: Identify the user who is making the request
    :param contact_id: int: Specify the id of the contact to be deleted
    :param db: Session: Pass the database session to the function
    :return: The contact that was removed
    :doc-author: Trelent
    """
    contact = await get_contact_by_id(user, contact_id, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def set_favorite(user: User, contact_id: int, body: ContactFavoriteModel, db: Session):
    """
    The set_favorite function sets the favorite status of a contact.
        Args:
            user (User): The user who is making the request.
            contact_id (int): The ID of the contact to set as a favorite or not.
            body (ContactFavoriteModel): A model containing whether or not to set this as a favorite, and if so, what type of favoriting it should be.
    
    :param user: User: Get the user id from the token
    :param contact_id: int: Get the contact from the database
    :param body: ContactFavoriteModel: Pass the is_favorite value to the function
    :param db: Session: Pass the database session to the function
    :return: A contact
    :doc-author: Trelent
    """
    contact = await get_contact_by_id(user, contact_id, db)
    if contact:
        contact.is_favorite = body.is_favorite
        db.commit()
    return contact