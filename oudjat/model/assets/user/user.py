import re
from typing import Dict, Union

from ..asset import Asset
from ..asset_type import AssetType
from .definitions import EMAIL_REG


class User(Asset):
    """A common class for users"""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(
        self,
        id: Union[int, str],
        name: str,
        firstname: str,
        lastname: str,
        login: str,
        email: str = None,
        description: str = None,
    ):
        """Constructor"""

        super().__init__(
            id=id, name=name, label=login, description=description, asset_type=AssetType.USER
        )

        self.firstname = firstname
        self.lastname = lastname

        self.email = None
        self.set_email(email)

        self.login = login
        self.user_type = None

    # ****************************************************************
    # Methods

    def get_firstname(self) -> str:
        """Getter for the user's firstname"""
        return self.firstname

    def get_lastname(self) -> str:
        """Getter for the user's lastname"""
        return self.lastname

    def get_email(self) -> str:
        """Getter for the user's email address"""
        return self.email

    def get_login(self) -> str:
        """Getter for the user's login"""
        return self.login

    def set_email(self, email: str) -> None:
        """Setter for the user's email address"""
        if email is None:
            return

        if re.match(EMAIL_REG, email):
            self.email = email

    def to_dict(self) -> Dict:
        """Converts the current instance into a dictionary"""
        asset_dict = super().to_dict()
        asset_dict.pop("label")

        return {
            **asset_dict,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "login": self.login,
            "type": self.user_type,
        }
