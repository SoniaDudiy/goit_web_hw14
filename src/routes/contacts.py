from typing import List

from fastapi import Depends, HTTPException, status, Path, APIRouter, Query
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role
from src.repository import contacts as repository_contacts
from src.schemas import ContactResponse, ContactModel, ContactFavoriteModel
from src.services.auth import auth_service
from src.services.role import RoleAccess


router = APIRouter(prefix="/api/contacts", tags=['contacts'])

allowed_operation_get = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_create = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_update = RoleAccess([Role.admin, Role.moderator])
allowed_operation_remove = RoleAccess([Role.admin])


@router.get("/", response_model=List[ContactResponse], dependencies=[Depends(allowed_operation_get)])
async def get_contacts(limit: int = Query(10, le=500), offset: int = 0, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts function returns a list of contacts for the current user.
        The limit and offset parameters are used to paginate the results.
    
    
    :param limit: int: Limit the number of contacts returned
    :param le: Limit the number of contacts that can be returned at one time
    :param offset: int: Skip the first offset number of contacts
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts(current_user, limit, offset, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(allowed_operation_get)])
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function returns a contact by id.
        Args:
            contact_id (int): The id of the contact to return.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).
            current_user (User, optional): User object from auth middleware. Defaults to Depends(auth_service.get_current_user).
    
    :param contact_id: int: Get the contact id from the url
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the database
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_id(current_user, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_operation_create)])
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.
        The function takes a ContactModel object as input, and returns the newly created contact.
    
    :param body: ContactModel: Pass the data from the request body to the function
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the database
    :return: The contact object, which is the same as the body
    :doc-author: Trelent
    """
    contact = await repository_contacts.create(current_user, body, db)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(allowed_operation_update)],
            description='Only moderators and admin')
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        The function takes an id and a body as input, and returns the updated contact.
        If no such contact exists, it raises an HTTPException with status code 404.
    
    :param body: ContactModel: Get the data from the request body
    :param contact_id: int: Get the contact id from the url
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the user who is making the request
    :return: A contactmodel object
    :doc-author: Trelent
    """
    contact = await repository_contacts.update(current_user, contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(allowed_operation_remove)])
async def remove_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The remove_contact function removes a contact from the database.
        Args:
            contact_id (int): The id of the contact to be removed.
            db (Session): A connection to the database.
            current_user (User): The user who is making this request, as determined by auth_service's get_current_user function.
        Returns: 
            Contact: The deleted Contact object.
    
    :param contact_id: int: Identify the contact to be removed
    :param db: Session: Get the database session
    :param current_user: User: Get the user from the database
    :return: The contact that was removed
    :doc-author: Trelent
    """
    contact = await repository_contacts.remove(current_user, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact


@router.patch("/{contact_id}/favorite", response_model=ContactResponse,
              dependencies=[Depends(allowed_operation_update)])
async def favorite_contact(body: ContactFavoriteModel, contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                           current_user: User = Depends(auth_service.get_current_user)):
    """
    The favorite_contact function is used to set a contact as favorite or not.
        The function takes in the following parameters:
            body: ContactFavoriteModel - A model containing the new favorite status of a contact.
            contact_id: int = Path(ge=0) - The id of the contact that will be updated.
            db: Session = Depends(get_db) - An instance of an open database session, which is passed into this function by dependency injection via FastAPI's Dependency Injection system (see https://fastapi.tiangolo.com/advanced/dependencies/#dependency
    
    :param body: ContactFavoriteModel: Pass the data from the request body to the function
    :param contact_id: int: Get the contact id from the url
    :param db: Session: Pass the database connection to the function
    :param current_user: User: Get the current user from the database
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.set_favorite(current_user, contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contact