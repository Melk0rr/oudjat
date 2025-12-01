"""A module to describe generic properties shared by more specific account objects like user or computer."""

from abc import ABC
from datetime import datetime
from enum import IntEnum
from typing import TYPE_CHECKING, Any, override

from oudjat.utils.time_utils import DateFlag, DateFormat, TimeConverter

from ..ldap_object import LDAPObject
from .ldap_account_flags import LDAPAccountFlag

if TYPE_CHECKING:
    from ..ldap_entry import LDAPEntry
    from ..ldap_object import LDAPCapabilities


class LDAPAccountStatus(IntEnum):
    """
    A helper class to handle LDAPAccount status.
    """

    UNKNOWN = -1
    DISABLED = 0
    ENABLED = 1

    @override
    def __str__(self) -> str:
        """
        Convert an LDAPAccountStatus into a string.

        Returns:
            str: A string represenation of an LDAPAccountStatus
        """

        return self.name


class LDAPAccount(LDAPObject, ABC):
    """A class to describe generic LDAP account objects."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self, ldap_entry: "LDAPEntry", capabilities: "LDAPCapabilities", **kwargs: Any
    ) -> None:
        """
        Initialize an LDAP Entry-based object with specific handling for user accounts.

        This method initializes the object using data from an `LDAPEntry` instance.
        It performs additional checks to determine account status based on the presence of certain properties like 'userAccountControl'.
        Additional flags are derived from the 'userAccountControl' property or its Microsoft equivalent (controlled by MS_ACCOUNT_CTL_PROPERTY).

        Args:
            ldap_entry (LDAPEntry)         : An instance of an LDAP entry containing relevant data for user accounts.
            capabilities (LDAPCapabilities): LDAP capabilities which provide ways for an LDAP object to interact with an LDAP server through an LDAPConnector
            kwargs (Any)                   : Any further arguments
        """

        super().__init__(ldap_entry=ldap_entry, capabilities=capabilities, **kwargs)

        self._status: "LDAPAccountStatus" = LDAPAccountStatus.UNKNOWN
        self._pwd_expires: bool = True
        self._pwd_expired: bool = False
        self._pwd_required: bool = True
        self._is_locked: bool = False

        self._account_flags: set[str] = set()

        if self.account_ctl is not None:
            self._status = LDAPAccountStatus(not LDAPAccountFlag.is_disabled(self.account_ctl))
            self._pwd_expires = LDAPAccountFlag.pwd_expires(self.account_ctl)
            self._pwd_expired = LDAPAccountFlag.pwd_expired(self.account_ctl)
            self._pwd_required = LDAPAccountFlag.pwd_required(self.account_ctl)
            self._is_locked = LDAPAccountFlag.is_locked(self.account_ctl)

            for flag in list(LDAPAccountFlag):
                if LDAPAccountFlag.check_flag(self.account_ctl, flag):
                    self.account_flags.add(flag.name)

        else:
            self._ldap_obj_flags.add("MISSING-USR-ACC-CTL")

    # ****************************************************************
    # Methods

    @property
    def san(self) -> str:
        """
        Return the sAMAccountName attribute of the current account.

        Returns:
            str: The value of the sAMAccountName attribute from the entry dictionary.
        """

        return self.entry.get("sAMAccountName")

    @property
    def status(self) -> "LDAPAccountStatus":
        """
        Return the account status.

        Returns:
            str: "Enabled" if the account is enabled, otherwise "Disabled".
        """

        return self._status

    @property
    def account_ctl(self) -> int | None:
        """
        Return the userAccountControl property of the current account.

        The userAccountControl is a bit flag that hosts multiple informations.
        See ldap_account_flags.py

        Returns:
            int | None: The userAccountControl represented by an int if present. Else None
        """

        return self.entry.get("userAccountControl", None)

    @property
    def account_expiration(self) -> datetime:
        """
        Return the account expiration date.

        Returns:
            datetime: The expiration date of the account as a datetime object, or a fixed year 9999 if it does not have an expiration.
        """

        default_acc_exp = self.entry.get("accountExpires")

        unified_acc_exp = datetime(9999, 12, 31, 23, 59, 59)
        if isinstance(default_acc_exp, datetime):
            unified_acc_exp = default_acc_exp

        elif isinstance(default_acc_exp, list):
            if len(default_acc_exp) > 0:
                unified_acc_exp = TimeConverter.str_to_date(default_acc_exp[0])

        else:
            unified_acc_exp = TimeConverter.str_to_date(default_acc_exp)

        return unified_acc_exp

    @property
    def last_logon(self) -> datetime | None:
        """
        Return the last logon datetime of the current account.

        Returns:
            datetime: The timestamp of the last logon as a datetime object.
        """

        return self.entry.get("lastLogonTimestamp")

    @property
    def last_logon_in_days(self) -> int:
        """
        Return the number of days since the current account last logged in.

        Returns:
            int: The difference in days between the current date and the last logon date.
        """

        return TimeConverter.days_diff(self.last_logon) if self.last_logon else -1

    @property
    def pwd_last_set(self) -> datetime | None:
        """
        Return the account password last set date.

        Returns:
            datetime: The timestamp of when the password was last set as a datetime object.
        """

        return self.entry.get("pwdLastSet", None)

    @property
    def pwd_last_set_timestp(self) -> float | None:
        """
        Return the timestamp of the last password set for this account.

        Returns:
            float | None: A float representation of the account last password change date. None if not present
        """

        return self.pwd_last_set.timestamp() if self.pwd_last_set is not None else None

    @property
    def pwd_last_set_in_days(self) -> int:
        """
        Return account password last set in days.

        Returns:
            int: The difference in days between the current date and the date when the password was last set.
        """

        return TimeConverter.days_diff(self.pwd_last_set) if self.pwd_last_set else -1

    @property
    def account_flags(self) -> set[str]:
        """
        Retrieve account flags.

        Returns:
            set[str]: A list of strings representing the account flags.
        """

        return self._account_flags

    @property
    def account_expires(self) -> bool:
        """
        Check whether the account expires.

        Returns:
            bool: True if the account does not expire (not year 9999), False otherwise.
        """

        return not self.account_expiration.year == 9999

    @property
    def pwd_required(self) -> bool:
        """
        Return weither the account requires a password.

        Returns:
            bool: True if a password is required, False otherwise.
        """

        return self._pwd_required

    @property
    def pwd_expires(self) -> bool:
        """
        Return weither the account's password expires.

        Returns:
            bool: True if the password is set to expire, False otherwise.
        """

        return self._pwd_expires

    @property
    def pwd_expired(self) -> bool:
        """
        Return weither the account password is expired.

        Returns:
            bool: True if the password has expired, False otherwise.
        """

        return self._pwd_expired

    @property
    def is_locked(self) -> bool:
        """
        Return whether or not the account is locked down.

        Returns:
            bool: True if the account is locked. False otherwise
        """

        return self._is_locked

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dict.

        Returns:
            dict[str, Any]: A dictionary containing various account details including sAMAccountName, status, expiration date, etc.
        """

        base_dict = super().to_dict()
        return {
            **base_dict,
            "san": self.san,
            "status": self.status,
            "account": {
                "status": str(self._status),
                "expires": self.account_expires,
                "expirationDate": LDAPAccount._format_acc_date_str(self.account_expiration),
                "ctl": self.account_ctl,
                "flags": list(self.account_flags),
            },
            "pwd": {
                "expires": self.pwd_expires,
                "expired": self.pwd_expired,
                "required": self.pwd_required,
                "lastSet": LDAPAccount._format_acc_date_str(self.pwd_last_set),
                "lastSetDays": self.pwd_last_set_in_days,
            },
            "logon": {
                "lastLogon": LDAPAccount._format_acc_date_str(self.last_logon),
                "lastLogonDays": self.last_logon_in_days,
            },
        }

    # ****************************************************************
    # Static methods

    @staticmethod
    def _format_acc_date_str(date: datetime | None) -> str:
        """
        Convert an account date into a readable string.

        Args:
            date (datetime): date to convert into a readable string

        Returns:
            str: readable formated string
        """

        if date is None:
            return ""

        return TimeConverter.date_to_str(date, date_format=DateFormat.from_flag(DateFlag.YMD_HMS))
