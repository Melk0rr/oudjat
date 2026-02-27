"""A module to handle LDAPUser manipulations."""

from typing import TYPE_CHECKING, Any, override

from oudjat.connectors.ldap.objects.account.ms_exch_flags import MSExchFlag

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
        ms_acc_ctl = self.ms_account_ctl["value"]
        if ms_acc_ctl is not None:
            self._enabled: bool = not LDAPAccountFlag.is_disabled(ms_acc_ctl)
            self._pwd_expires: bool = LDAPAccountFlag.pwd_expires(ms_acc_ctl)
            self._pwd_expired: bool = LDAPAccountFlag.pwd_expired(ms_acc_ctl)
            self._pwd_required: bool = LDAPAccountFlag.pwd_required(ms_acc_ctl)
            self._is_locked: bool = LDAPAccountFlag.is_locked(ms_acc_ctl)

            self._account_flags.update(LDAPAccountFlag.flags(ms_acc_ctl))

    # ****************************************************************
    # Methods - getters/setters

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

    # ****************************************************************
    # Methods - getters/setters for AD context

    @property
    def ms_account_ctl(self) -> dict[str, Any]:
        """
        Return the AD specific account control property.

        This property contains additional computed bits over the base userAccountControl.
        Available only in Active Directory.

        Returns:
            dict[str, Any]: The computed account control details dictionary
        """

        details = {}
        details["attr"] = "msDS-User-Account-Control-Computed"
        details["value"] = self.entry.get(details["attr"])

        return details

    @property
    def ms_exchange_recipient_details(self) -> dict[str, Any]:
        """
        Return Exchange recipient type details.

        Available only in Active Directory.

        Returns:
            dict[str, Any]: Exchange recipient type details dictionary
        """

        details = {}

        details["attr"] = "msExchRecipientTypeDetails"
        details["value"] = self.entry.get(details["attr"])
        details["flags"] = set()

        if details["value"] is not None:
            details["flags"].update(MSExchFlag.flags(details["value"]))

        details["flags"] = list(details["flags"])

        return details

    @property
    def pso(self) -> str:
        """
        Return the password settings for the current user .

        Available only in Active Directory.

        Returns:
            str: Password setting string
        """

        return self.entry.get("msDS-ResultantPSO")

    # ****************************************************************
    # Methods - convertes

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            dict[str, Any]: The current user represented as a dictionary
        """

        base = super().to_dict()
        ms_acc_ctl = self.ms_account_ctl
        base["account"][ms_acc_ctl["attr"]] = ms_acc_ctl["value"]

        exch_details = self.ms_exchange_recipient_details
        exch_details.pop("attr")

        return {
            **base,
            "givenname": self.givenname,
            "surname": self.surname,
            "email": self.email,
            "employeeId": self.employee_id,
            "manager": self.manager,
            "isAdmin": self.is_admin,
            "exchange": exch_details,
            "extensionAttributes": self.extension_attr,
        }
