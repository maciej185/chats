"""CRUD operations for the auth package."""

from pathlib import Path
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.models import DB_Profile, DB_User
from src.roles import Roles

from .models import ProfileAdd, ProfileUpdate, UserAdd
from .utils import get_password_hash


def create_user(
    db: Session, user_data: UserAdd, profile_data: ProfileAdd, role: int = Roles.USER.value
) -> DB_User:
    """Save User and return it's DB representation.

    Args:
        db: An instance of the sqlalchemy.orm.Session, representning the current
            DB session.
        user_data: Pydantic model with the data that will be used to save the
                    new user in the DB.
        profile_data: Pydantic model with data that will be used to create the
                        profile for the newly registered user.
        role: Value of the 'role' columns in the 'users' table

    Raises:
        HTTPException: Raised when a user with the given username already exists in the
                        DB.

    Returns:
        An instance of the DB_User model, representing the newly created user.
    """
    hashed_password = get_password_hash(user_data.plain_text_password)
    db_user = DB_User(
        username=user_data.username,
        hashed_password=hashed_password,
        email=user_data.email,
        role=role,
    )
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email taken."
        )
    db.refresh(db_user)
    create_profile(db=db, profile_data=profile_data, user_id=db_user.user_id)
    return db_user


def create_profile(db: Session, profile_data: ProfileAdd, user_id: int) -> DB_Profile:
    """Create a new profile for the given User.

    Args:
        db: An instance of the sqlalchemy.orm.Session, representning the current
            DB session.
        profile_data: An instance of the pydantic ProfileAdd model with data
                        that will be used to create a profile for the given user.
        user_id: ID of the user for whom a new profile will be created in the DB.

    Returns:
        An instance of the DB_Profile class, representing newly created profile
        for a user with the given ID.
    """
    db_profile = DB_Profile(**profile_data.model_dump(), user_id=user_id)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


def update_profile_in_db(
    db: Session, user_id: int, profile_data: ProfileUpdate
) -> Optional[DB_Profile]:
    """Update the given User's profile with the provided information.

    Args:
        user_id: ID of the given user in the DB.
        profile_data: An instance of the pydantic UserUpdate model with the new
                    information about the user.

    Raises:
        HTTPException: Raised when the profile with the given ID was
                        not found in the DB.
    Returns:
        Updated instance of the DB_Profile model if there was any valid data provided,
        None otherwise.
    """
    db_profile_query = db.query(DB_Profile).filter(DB_Profile.user_id == user_id)
    if not db_profile_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile with the given ID was not found in the DB.",
        )
    if db_profile_query:
        profile_dict = {k: v for k, v in profile_data.model_dump().items() if not v is None}
        db_profile_query.update(profile_dict, synchronize_session=False)
        db.commit()
        db_profile = db_profile_query.first()
        db.refresh(db_profile)
        return db_profile


def delete_user_from_db(db: Session, user_id: int) -> None:
    """Delete user with the given ID from DB.

    Args:
        db: Instance of the sqlalchemy.orm.Session class,
            representing the current DB session.
        user_id: ID of the user that is meant to be deleted.

    Raises:
        HTTPException: Raised when the user with the given ID was
                        not found in the DB.

    """
    user = db.query(DB_User).filter(DB_User.user_id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with the given ID was not found in the DB.",
        )
    db.delete(user)
    db.commit()


def get_all_users_from_db(db: Session) -> list[DB_User]:
    """List all users in the DB.

    Args:
        db: Instance of the sqlalchemy.orm.Session class,
            representing the current DB session.

    Returns:
        A list with instances of the DB_User model.
    """
    return db.query(DB_User).all()


def get_user_from_db(db: Session, user_id: int) -> DB_User:
    """Get a specific user from the DB.

    Args:
        db: Instance of the sqlalchemy.orm.Session class,
            representing the current DB session.
        user_id: ID of the user that is meant to be fetched.

    Raises:
        HTTPException: Raised when the user with the given ID was
                        not found in the DB.
    """
    user = db.query(DB_User).filter(DB_User.user_id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=404, detail="User with the given ID does not exist in the DB."
        )
    return user


def get_profile_from_db(db: Session, profile_id: int) -> DB_Profile:
    """Get a specific profile from the DB.

    Args:
        db: Instance of the sqlalchemy.orm.Session class,
            representing the current DB session.
        profile_id: ID of the profile that is meant to be fetched.

    Raises:
        HTTPException: Raised when the profile with the given ID was
                        not found in the DB.
    """
    profile = db.query(DB_Profile).filter(DB_Profile.user_id == profile_id).first()
    if profile is None:
        raise HTTPException(
            status_code=404, detail="Profile with the given ID does not exist in the DB."
        )
    return profile


def update_users_profile_pic_path(db: Session, user_id: int, profile_pic_path: Path) -> DB_User:
    """Update given user's profile pic path and return refreshed user object.

    Args:
        db: Instance of the sqlalchemy.orm.Session class,
            representing the current DB session.
        user_id: ID of the user that is meant to have their
                    profile picture updated.
        profile_pic_path: Instance of the pathlib.Path class with the
                            location of the user's new profile picture.

    Raises:
        HTTPException: Raised when the user with the given ID
                        is not found in the DB.

    Returns:
        Refreshed instance of the DB_User model.
    """
    db_user = db.query(DB_User).filter(DB_User.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with the given ID was not found in the DB.",
        )
    db_user.profile.profile_pic_path = str(profile_pic_path)
    db.commit()
    db.refresh(db_user)
    return db_user
