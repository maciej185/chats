"""CRUD operations for the auth package."""

from sqlalchemy.orm import Session
from .models import PasswordChangeData
from src.routes.auth.utils import get_password_hash
from src.db.models import DB_User


def update_password(db: Session, user: DB_User,  password_change_data: PasswordChangeData) -> None:
    """Update password of the user with the provided ID.
    
    Args:
        db: An instance of the sqlalchemy.orm.Session, representning the current
            DB session.
        user: An instance of the DB_User class, representing the currently logged in 
            user whose password is meant to be updated.
        password_change_data: Instance of the PasswordChangeData model containing 
            the new password.
    """
    user.hashed_password = get_password_hash(password_change_data.plain_text_password)
    db.commit()