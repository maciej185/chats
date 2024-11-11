"""Pydantic models for the auth package."""

from pydantic import BaseModel

class PasswordChangeData(BaseModel):
    """Model with info for changing a password."""
    plain_text_password: str