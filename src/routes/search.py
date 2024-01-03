from typing import List

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import search as repository_contacts
from src.schemas import ContactResponse
from src.services.auth import auth_service

search = APIRouter(prefix="/api/search", tags=['search'])


@search.get("/shift/{shift}", response_model=List[ContactResponse])
async def get_birthday_list(shift: int, db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_birthday_list(current_user, shift, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contacts


@search.get("/find/{partial_info}", response_model=List[ContactResponse],
            description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def find_contacts_by_partial_info(partial_info: str, db: Session = Depends(get_db),
                                  current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_users_by_partial_info(current_user, partial_info, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")
    return contacts

@search.get("/shift/{shift}", response_model=List[ContactResponse])
async def get_birthday_list(shift: int, db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_birthday_list(current_user, shift, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return contacts