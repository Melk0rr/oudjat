"""A module that defines the user asset type."""

import re
from typing import Any, override

from ..asset import Asset
from ..asset_type import AssetType
from .definitions import EMAIL_REG


class User(Asset):
    """A common class for users."""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(
        self,
        user_id: int | str,
        name: str,
        firstname: str,
        lastname: str,
        login: str,
        email: str | None = None,
        description: str | None = None,
    ) -> None:
        """
        Create a new instance of User.

        Initializes a new instance of the User class with the provided parameters.

        Args:
            user_id (Union[int, str])  : the unique identifier for the user.
            name (str)                 : the full name of the user.
            firstname (str)            : the first name of the user.
            lastname (str)             : the last name of the user.
            login (str)                : the login username for the user.
            email (str, optional)      : the email address of the user. Defaults to None.
            description (str, optional): a description or bio for the user. Defaults to None.
        """

        super().__init__(
            asset_id=user_id,
            name=name,
            label=login,
            description=description,
            asset_type=AssetType.USER,
        )

        self.firstname: str = firstname
        self.lastname: str = lastname

        self.email: str | None = None
        if email is not None:
            self.set_email(email)

        self.login: str = login

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

    def get_email(self) -> str | None:
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

        if re.match(EMAIL_REG, email):
            self.email = email

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

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
            # "type": self.user_type,
        }
