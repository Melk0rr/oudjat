"""An asset sub package that focuses on users."""

from .definitions import EMAIL_REG
from .user import User

__all__ = ["User", "EMAIL_REG"]
