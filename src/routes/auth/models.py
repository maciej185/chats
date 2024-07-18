"""Pydantic models for the auth package."""

from datetime import date
from typing import Any

from pydantic import BaseModel

from src.roles import Roles


class ProfileBase(BaseModel):
    """Base for Profile models."""

    first_name: str
    last_name: str
    date_of_birth: date


class ProfileAdd(ProfileBase):
    """Model for creating a new profile."""


class Profile(ProfileBase):
    """Model with all relevant Profile info."""

    user_id: int


class ProfileUpdate(ProfileBase):
    """Model for updating the User info."""

    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None


class UserBase(BaseModel):
    """Base for User models."""

    username: str
    email: str

    class Config:
        from_attributes = True


class UserAdd(UserBase):
    """Model for adding users."""

    plain_text_password: str


class UserInResponse(UserBase):
    """Model for returning User information."""

    user_id: int
    role: Roles
    profile: list[Profile] | Profile

    def model_post_init(self, __context: Any) -> None:
        """Swap a one-element list of Profile instances for a single Profile.

        Since the model instance is create from an sqlalchemy model (as indiciated
        by the 'from_attributes' parameter in the config) any foreign key relationship
        is by default one-to-many and demands a use of list for the child objects. There
        is however always only one Profile relating to a given User and so it makes sense
        and is safe (guaranteed to not result in an error) to swap the list for a single
        model instance.
        """
        self.profile = self.profile[0]
        return super().model_post_init(__context)


class Token(BaseModel):
    """Model with token information."""

    access_token: str
    token_type: str
