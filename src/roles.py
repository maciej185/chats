"""User roles available in the app."""

from enum import Enum


class Roles(Enum):
    """Enum storing roles available in the system."""

    USER = 0
    ADMIN = 1
