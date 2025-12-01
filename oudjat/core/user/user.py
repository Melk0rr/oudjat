"""A module that defines the user asset type."""

import re
from typing import Any, TypedDict, override

from oudjat.utils.mail import EMAIL_REG

from ..asset import Asset
from ..asset_type import AssetType
from .user_type import UserType


class UserBaseDict(TypedDict):
    """
    A simpler helper class to properly handle user base dictionary attributes.

    Attributes:
        login (str)           : The login of the user
        firstname (str | None): The firstname of the user, if any
        lastname (str | None) : The lastname of the user, if any
        email (str | None)    : The firstname of the user, if any
        userType (UserType)   : The type of the user
    """

    login: str
    firstname: str | None
    lastname: str | None
    email: str | None
    userType: "UserType"


class User(Asset):
    """A common class for users."""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(
        self,
        user_id: int | str,
        name: str,
        login: str,
        firstname: str | None = None,
        lastname: str | None = None,
        email: str | None = None,
        user_type: "str | UserType | None" = None,
        description: str | None = None,
    ) -> None:
        """
        Create a new instance of User.

        Initializes a new instance of the User class with the provided parameters.

        Args:
            user_id (int | str)              : The unique identifier for the user.
            name (str)                       : The full name of the user.
            firstname (str)                  : The first name of the user.
            lastname (str)                   : The last name of the user.
            login (str)                      : The login username for the user.
            email (str | None)               : The email address of the user. Defaults to None.
            user_type (str | UserType | None): The type of the user
            description (str | None)         : A description or bio for the user. Defaults to None.
        """

        super().__init__(
            asset_id=user_id,
            name=name,
            label=login,
            description=description,
            asset_type=AssetType.USER,
        )

        self._firstname: str | None = firstname
        self._lastname: str | None = lastname

        self._email: str | None = None
        if email is not None:
            self.email = email

        if user_type is None or (
            isinstance(user_type, str) and user_type.upper() in UserType._member_names_
        ):
            user_type = UserType.UNKNOWN

        else:
            user_type = UserType(user_type)

        self._user_type: "UserType" = user_type
        self._login: str = login

    # ****************************************************************
    # Methods

    @property
    def firstname(self) -> str | None:
        """
        Getter for the user's firstname.

        Returns:
            str: The first name of the user.
        """

        return self._firstname

    @property
    def lastname(self) -> str | None:
        """
        Getter for the user's lastname.

        Returns:
            str: The last name of the user.
        """

        return self._lastname

    @property
    def email(self) -> str | None:
        """
        Getter for the user's email address.

        Returns:
            str: The email address of the user.
        """

        return self._email

    @email.setter
    def email(self, email: str) -> None:
        """
        Setter for the user's email address.

        Args:
            email (str): The new email address to be set.
        """

        if re.match(EMAIL_REG, email):
            self._email = email

    @property
    def login(self) -> str:
        """
        Getter for the user's login.

        Returns:
            str: The login username for the user.
        """

        return self._login

    @property
    def user_type(self) -> "UserType":
        """
        Return the type of the current user.

        Returns:
            UserType: The type of the current user
        """

        return self._user_type

    @user_type.setter
    def user_type(self, new_user_type: "UserType") -> None:
        """
        Set a new user type value for the current user.

        Args:
            new_user_type (UserType): The new user type
        """

        self._user_type = new_user_type

    @override
    def __str__(self) -> str:
        """
        Return a string representation of the instance.

        Returns:
            str: the current user represented by a string

        Example:
            rick = User(firstname="Roy", lastname="Batty", login="r.batty"...)
            print(rick) -> "r.batty"
        """

        return self._login

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            dict[str, Any]: A dictionary representation of the User instance.
        """

        asset_dict = super().to_dict()
        _ = asset_dict.pop("label")

        base_dict = {
            "firstname": self._firstname,
            "lastname": self._lastname,
            "email": self._email,
            "login": self._login,
            "userType": str(self._user_type)
        }

        return {
            **asset_dict,
            **base_dict,
        }
