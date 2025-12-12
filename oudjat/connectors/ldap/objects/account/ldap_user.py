"""A module to handle LDAPUser manipulations."""

from typing import TYPE_CHECKING, Any, override

from oudjat.connectors.ldap.objects.account.ms_exch_flags import MSExchFlag
from oudjat.core.user import User

from .definitions import MS_ACCOUNT_CTL, MS_EXCH_RECIPIENT
from .ldap_account import LDAPAccount
from .ldap_account_flags import LDAPAccountFlag

if TYPE_CHECKING:
    from ..ldap_entry import LDAPEntry


class LDAPUser(LDAPAccount):
    """A class to describe LDAP user objects."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, ldap_entry: "LDAPEntry", **kwargs: Any) -> None:
        """
        Create a new instance of LDAPUser.

        Args:
            ldap_entry (LDAPEntry): Base dictionary entry
            **kwargs (Any)        : Any further argument to pass to parent class
        """

        super().__init__(ldap_entry=ldap_entry, **kwargs)

        # Check additional account control bits
        # see https://learn.microsoft.com/en-us/windows/win32/adschema/a-msds-user-account-control-computed
        if self.ms_account_ctl is not None:
            self._enabled: bool = not LDAPAccountFlag.is_disabled(self.ms_account_ctl)
            self._pwd_expires: bool = LDAPAccountFlag.pwd_expires(self.ms_account_ctl)
            self._pwd_expired: bool = LDAPAccountFlag.pwd_expired(self.ms_account_ctl)
            self._pwd_required: bool = LDAPAccountFlag.pwd_required(self.ms_account_ctl)
            self._is_locked: bool = LDAPAccountFlag.is_locked(self.ms_account_ctl)

            self._account_flags.update(LDAPAccountFlag.flags(self.ms_account_ctl))

        self._exchange_flags: set[str] = set()
        if self.ms_exchange_recipient_details is not None:
            self._exchange_flags.update(MSExchFlag.flags(self.ms_exchange_recipient_details))

        self._user: "User" = User(
            user_id=self.id,
            name=self.name,
            firstname=self.givenname,
            lastname=self.surname,
            email=self.email,
            login=self.san,
            description=self.description,
        )

    # ****************************************************************
    # Methods

    @property
    def givenname(self) -> str:
        """
        Return the given name (firstname) of a user object.

        Returns:
            str: The given name of the user
        """

        return self.entry.get("givenName")

    @property
    def surname(self) -> str:
        """
        Return the surname (lastname / family name) of a user object.

        Returns:
            str: The lastname of the user
        """

        return self.entry.get("sn")

    @property
    def email(self) -> str:
        """
        Return the email address of the current user object.

        Returns:
            str: Email string of the current user
        """

        email = self.entry.get("mail", None)
        if email is not None:
            email = email.lower()

        return email

    @property
    def ms_account_ctl(self) -> int | None:
        """
        Return the AD specific account control property.

        This property contains additional computed bits over the base userAccountControl.

        Returns:
            int | None: The computed account control as a bit flag
        """

        return self.entry.get(MS_ACCOUNT_CTL)

    @property
    def ms_exchange_recipient_details(self) -> int | None:
        """
        Return the Exchange recipient type stored as a bitmask.

        Returns:
            int | None: The bitmask giving Exchange recipient type details if set
        """

        return self.entry.get(MS_EXCH_RECIPIENT)

    @property
    def employee_id(self) -> str:
        """
        Return the employee id.

        Returns:
            str: employee id
        """

        return self.entry.get("employeeID", None)

    @property
    def manager(self) -> str:
        """
        Return the user's manager.

        Returns:
            str: a ref to the user's manager
        """

        return self.entry.get("manager", None)

    @property
    def extension_attr(self) -> dict[str, Any]:
        """
        Return a dictionary of the user extension attributes if there is any.

        Returns:
            dict[str, Any]: A dictionary of extension attributes
        """

        extension_attr = {}
        for i in range(1, 16):
            attr_i = self.entry.get(f"extensionAttribute{i}", None)
            if attr_i is not None:
                extension_attr[f"extensionAttribute{i}"] = attr_i

        return extension_attr

    @property
    def is_admin(self) -> bool:
        """
        Check if the current user is an admin.

        Returns:
            bool: True if the current user is admin. False otherwise
        """

        is_admin = False
        adm_count = self.entry.get("adminCount", None)

        if adm_count is not None:
            is_admin = adm_count == 1

        return is_admin

    def to_user(self) -> "User":
        """
        Convert the current LDAPUser into a regular User instance.

        Returns:
            User: A regular User instance based on the current LDAPUser
        """

        usr = self._user
        usr.add_custom_attr("ldap", self.ldap_dict())

        return usr

    def ldap_dict(self) -> dict[str, Any]:
        """
        Return a dictionary of the LDAP properties.

        Returns:
            dict[str, Any]: A dictionary of the user LDAP properties
        """

        base = super().to_dict()
        base["account"][MS_ACCOUNT_CTL] = self.ms_account_ctl
        return {
            **base,
            "employeeId": self.employee_id,
            "manager": self.manager,
            "isAdmin": self.is_admin,
            "exchange": {
                "recipientDetails": self.ms_exchange_recipient_details,
                "flags": list(self._exchange_flags)
            },
            "extensionAttributes": self.extension_attr,
        }

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            dict[str, Any]: The current user represented as a dictionary
        """

        return {**self.ldap_dict(), **self._user.to_dict()}
