import datetime

from pydantic import BaseModel, Field, EmailStr

from src.database.models import Role

class ContactModel(BaseModel):
    firstname: str = Field(default='Unknown', min_length=1, max_length=50)
    lastname: str = Field(default='Unknown', min_length=2, max_length=50)
    email: EmailStr
    phone: str = Field(default='+38091534167', min_length=10, max_length=15)
    birthday: datetime.date = Field(default='2023-01-09')
    is_favorite: bool = False


class ContactFavoriteModel(BaseModel):
    is_favorite: bool = False


class ContactResponse(BaseModel):
    id: int
    firstname: str
    lastname: str
    email: EmailStr
    phone: str
    birthday: datetime.date
    is_favorite: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True

class UserModel(BaseModel):
    username: str = Field(min_length=4, max_length=12)
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    avatar: str
    roles: Role
    created_at: datetime.datetime | None
    updated_at: datetime.datetime | None

    class Config:
        orm_mode = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RequestEmail(BaseModel):
    email: EmailStr


class UserInDB(UserModel):
    hashed_password: str


class ResetPassword(BaseModel):
    reset_password_token: str
    new_password: str
    confirm_password: str   