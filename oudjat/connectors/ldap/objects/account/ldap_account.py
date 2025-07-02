"""A module to describe generic properties shared by more specific account objects like user or computer."""

from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Set

from oudjat.utils.time_utils import DateFlag, DateFormat, TimeConverter

from ..ldap_object import LDAPObject
from .ldap_account_flags import LDAPAccountFlag

if TYPE_CHECKING:
    from ..ldap_entry import LDAPEntry


def acc_date_str(date: datetime) -> str:
    """
    Convert an account date into a readable string.

    Args:
        date (datetime): date to convert into a readable string

    Returns:
        str: readable formated string
    """

    return TimeConverter.date_to_str(date, date_format=DateFormat.from_flag(DateFlag.YMD_HMS))


class LDAPAccount(LDAPObject):
    """A class to describe generic LDAP account objects."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, ldap_entry: "LDAPEntry"):
        """
        Initialize an LDAP Entry-based object with specific handling for user accounts.

        This method initializes the object using data from an `LDAPEntry` instance and performs additional checks to determine account status based on the presence of certain properties like 'userAccountControl'. Additional flags are derived from the 'userAccountControl' property or its Microsoft equivalent (controlled by MS_ACCOUNT_CTL_PROPERTY).

        Args:
            ldap_entry (LDAPEntry): An instance of an LDAP entry containing relevant data for user accounts.

        Returns:
            None
        """

        super().__init__(ldap_entry=ldap_entry)

        pwd_last_set = self.get_pwd_last_set()
        self.pwd_last_set_timestp = pwd_last_set.timestamp() if pwd_last_set is not None else None

        self.account_control = self.entry.get("userAccountControl", None)

        self.enabled = True
        self.pwd_expires = True
        self.pwd_expired = False
        self.pwd_required = True
        self.is_locked = False
        self.account_flags: Set[str] = set()

        if self.account_control is not None:
            self.enabled = not LDAPAccountFlag.is_disabled(self.account_control)
            self.pwd_expires = LDAPAccountFlag.pwd_expires(self.account_control)
            self.pwd_expired = LDAPAccountFlag.pwd_expired(self.account_control)
            self.pwd_required = LDAPAccountFlag.pwd_required(self.account_control)
            self.is_locked = LDAPAccountFlag.is_locked(self.account_control)

            for flag in list(LDAPAccountFlag):
                if LDAPAccountFlag.check_flag(self.account_control, flag):
                    self.account_flags.add(flag.name)

        else:
            self.ldap_obj_flags.append("MISSING-USR-ACC-CTL")

    # ****************************************************************
    # Methods

    def get_san(self) -> str:
        """
        Return the sAMAccountName attribute of the current account.

        Returns:
            str: The value of the sAMAccountName attribute from the entry dictionary.
        """

        return self.entry.get("sAMAccountName")

    def is_enabled(self) -> bool:
        """
        Return whether the account is enabled or not.

        Returns:
            bool: True if the account is enabled, False otherwise.
        """

        return self.enabled

    def get_status(self) -> str:
        """
        Return the account status.

        Returns:
            str: "Enabled" if the account is enabled, otherwise "Disabled".
        """

        return "Enabled" if self.enabled else "Disabled"

    def get_account_expiration(self) -> datetime:
        """
        Return the account expiration date.

        Returns:
            datetime: The expiration date of the account as a datetime object, or a fixed year 9999 if it does not have an expiration.
        """

        default_acc_exp = self.entry.get("accountExpires")
        return (
            datetime(9999, 12, 31)
            if default_acc_exp is None
            or (isinstance(default_acc_exp, list) and len(default_acc_exp) == 0)
            else default_acc_exp
        )

    def get_last_logon(self) -> datetime:
        """
        Return the last logon datetime of the current account.

        Returns:
            datetime: The timestamp of the last logon as a datetime object.
        """

        return self.entry.get("lastLogonTimestamp")

    def get_last_logon_days(self) -> int:
        """
        Return the number of days since the current account last logged in.

        Returns:
            int: The difference in days between the current date and the last logon date.
        """

        return TimeConverter.days_diff(self.get_last_logon())

    def get_pwd_last_set(self) -> datetime:
        """
        Return the account password last set date.

        Returns:
            datetime: The timestamp of when the password was last set as a datetime object.
        """

        return self.entry.get("pwdLastSet", None)

    def get_pwd_last_set_days(self) -> int:
        """
        Return account password last set in days.

        Returns:
            int: The difference in days between the current date and the date when the password was last set.
        """

        return TimeConverter.days_diff(self.get_pwd_last_set())

    def get_account_flags(self) -> List[str]:
        """
        Retrieve account flags.

        Returns:
            List[str]: A list of strings representing the account flags.
        """

        return list(self.account_flags)

    def does_account_expires(self) -> bool:
        """
        Check whether the account expires.

        Returns:
            bool: True if the account does not expire (not year 9999), False otherwise.
        """

        return not self.get_account_expiration().year == 9999

    def does_pwd_expires(self) -> bool:
        """
        Return weither the account's password expires.

        Returns:
            bool: True if the password is set to expire, False otherwise.
        """

        return self.pwd_expires

    def is_pwd_expired(self) -> bool:
        """
        Return weither the account password is expired.

        Returns:
            bool: True if the password has expired, False otherwise.
        """

        return self.pwd_expired

    def to_dict(self) -> Dict:
        """
        Convert the current instance into a dict.

        Returns:
            Dict: A dictionary containing various account details including sAMAccountName, status, expiration date, etc.
        """

        base_dict = super().to_dict()
        return {
            **base_dict,
            "san": self.get_san(),
            "status": self.get_status(),
            "account_expires": self.does_account_expires(),
            "account_exp_date": acc_date_str(self.get_account_expiration()),
            "pwd_expires": self.pwd_expires,
            "pwd_expired": self.pwd_expired,
            "pwd_required": self.pwd_required,
            "last_logon": acc_date_str(self.get_last_logon()),
            "last_logon_days": self.get_last_logon_days(),
            "pwd_last_set": acc_date_str(self.get_pwd_last_set()),
            "pwd_last_set_days": self.get_pwd_last_set_days(),
            "account_ctl": self.account_control,
            "account_flags": "-".join(self.get_account_flags()),
        }
