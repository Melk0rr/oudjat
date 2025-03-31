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
        """
        Constructor for the User class.

        Initializes a new instance of the User class with the provided parameters.

        Args:
            id (Union[int, str]): The unique identifier for the user.
            name (str): The full name of the user.
            firstname (str): The first name of the user.
            lastname (str): The last name of the user.
            login (str): The login username for the user.
            email (str, optional): The email address of the user. Defaults to None.
            description (str, optional): A description or bio for the user. Defaults to None.
        """

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
        """
        Getter for the user's firstname.

        Returns:
            str: The first name of the user.
        """
        return self.firstname

    def get_lastname(self) -> str:
        """
        Getter for the user's lastname.

        Returns:
            str: The last name of the user.
        """
        return self.lastname

    def get_email(self) -> str:
        """
        Getter for the user's email address.

        Returns:
            str: The email address of the user.
        """
        return self.email

    def get_login(self) -> str:
        """
        Getter for the user's login.

        Returns:
            str: The login username for the user.
        """
        return self.login

    def set_email(self, email: str) -> None:
        """
        Setter for the user's email address.

        Args:
            email (str): The new email address to be set.
        """
        if email is None:
            return

        if re.match(EMAIL_REG, email):
            self.email = email

    def to_dict(self) -> Dict:
        """
        Converts the current instance into a dictionary.

        Returns:
            Dict: A dictionary representation of the User instance.
        """
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
