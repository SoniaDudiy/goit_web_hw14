from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    The get_user_by_email function returns a user object from the database if it exists, otherwise None.
    
    :param email: str: Specify the type of data that is expected to be passed into the function
    :param db: Session: Pass in the database session
    :return: A user object if the user exists, or none if it doesn't
    :doc-author: Trelent
    """
    return db.query(User).filter_by(email=email).first()


async def create_user(body: UserModel, db: Session):
    """
    The create_user function creates a new user in the database.
        It takes a UserModel object as input and returns the newly created user.
    
    :param body: UserModel: Pass in the user object that is created by the usermodel class
    :param db: Session: Connect to the database
    :return: A user object, which is then passed to the create_user_response function
    :doc-author: Trelent
    """
    g = Gravatar(body.email)

    new_user = User(**body.model_dump(), avatar=g.get_image())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, refresh_token, db: Session):
    """
    The update_token function updates the user's refresh token in the database.
        Args:
            user (User): The User object to update.
            refresh_token (str): The new refresh token for this user.
            db (Session): A database session to use for updating the User object.
    
    :param user: User: Pass in the user object that is currently logged in
    :param refresh_token: Update the user's refresh_token in the database
    :param db: Session: Update the database with the new refresh token
    :return: Nothing
    :doc-author: Trelent
    """
    user.refresh_token = refresh_token
    db.commit()

async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function sets the confirmed field of a user to True.
    
    :param email: str: Get the email of the user
    :param db: Session: Pass the database session to the function
    :return: None, but the type hint says it returns none
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.
    
    Args:
        email (str): The email address of the user to update.
        url (str): The URL for the new avatar image.
        db (Session, optional): A database session object to use instead of creating one locally. Defaults to None.  # noQA: E501 line too long, but this is an example!  # noQA: E501 line too long, but this is an example!  # noQA: E501 line too long, but this is an example!  # noQ
    
    :param email: Find the user in the database
    :param url: str: Specify the type of data that is passed into the function
    :param db: Session: Pass in the database session
    :return: A user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def update_password(user: User, new_password: str, db: Session) -> None:
    """
    The update_password function updates the password of a user in the database.
        Args:
            user (User): The User object to update.
            new_password (str): The new password for this User object.
            db (Session): A Session instance that is used to commit changes to the database.
    
    :param user: User: Pass the user object to the function
    :param new_password: str: Pass in the new password that will be set for the user
    :param db: Session: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user.password = new_password
    db.commit()


async def update_reset_token(user: User, reset_token, db: Session) -> None:
    """
    The update_reset_token function updates the password reset token for a user.
        Args:
            user (User): The User object to update.
            reset_token (str): The new password reset token to set for the user.
            db (Session): A database session instance, used to commit changes made by this function.
    
    :param user: User: Identify the user that is requesting a password reset
    :param reset_token: Update the password_reset_token column in the users table
    :param db: Session: Access the database
    :return: None
    :doc-author: Trelent
    """
    user.password_reset_token = reset_token
    db.commit()    