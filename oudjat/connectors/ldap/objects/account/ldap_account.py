from datetime import datetime
from typing import Dict, List

from oudjat.utils import DATE_TIME_FLAGS, date_format_from_flag, days_diff

from ..ldap_object import LDAPObject
from .definitions import MS_ACCOUNT_CTL_PROPERTY
from .ldap_account_flags import (
    LDAPAccountFlag,
    check_account_flag,
    is_disabled,
    pwd_expired,
    pwd_expires,
    pwd_required,
)


def acc_date_str(date: datetime) -> str:
    """Converts an account date into a string"""
    return date.strftime(date_format_from_flag(DATE_TIME_FLAGS))


class LDAPAccount(LDAPObject):
    """A class to describe generic LDAP account objects"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, ldap_entry: "LDAPEntry"):  # noqa: F821
        """
        Constructor for initializing an LDAP Entry-based object with specific handling for user accounts.

        This method initializes the object using data from an `LDAPEntry` instance and performs additional checks to determine account status based on the presence of certain properties like 'userAccountControl'. Additional flags are derived from the 'userAccountControl' property or its Microsoft equivalent (controlled by MS_ACCOUNT_CTL_PROPERTY).

        Args:
            ldap_entry (LDAPEntry): An instance of an LDAP entry containing relevant data for user accounts.

        Returns:
            None
        """

        super().__init__(ldap_entry=ldap_entry)

        self.pwd_last_set_timestp = self.get_pwd_last_set().timestamp()

        self.account_control = self.entry.get("userAccountControl", None)
        ms_acc_ctl = self.entry.get(MS_ACCOUNT_CTL_PROPERTY, None)

        self.enabled = True
        self.pwd_expires = False
        self.pwd_expired = False
        self.pwd_required = False
        self.account_flags = []

        if self.account_control is not None:
            self.enabled = not is_disabled(self.account_control)
            self.pwd_expires = pwd_expires(self.account_control)
            self.pwd_expired = pwd_expired(self.account_control)
            self.pwd_required = pwd_required(self.account_control)

            self.account_flags = [
                f.name
                for f in LDAPAccountFlag
                if check_account_flag(self.account_control, f)
                or (ms_acc_ctl is not None and check_account_flag(ms_acc_ctl, f))
            ]

        else:
            self.followup_flags.append("MISSING-USR-ACC-CTL")

    # ****************************************************************
    # Methods

    def get_san(self) -> str:
        """Getter for account sAMAccountName

        Returns:
            str: The value of the sAMAccountName attribute from the entry dictionary.
        """
        return self.entry.get("sAMAccountName")

    def is_enabled(self) -> bool:
        """Returns whether the account is enabled or not

        Returns:
            bool: True if the account is enabled, False otherwise.
        """
        return self.enabled

    def get_status(self) -> str:
        """Getter to retrieve account status

        Returns:
            str: "Enabled" if the account is enabled, otherwise "Disabled".
        """
        return "Enabled" if self.enabled else "Disabled"

    def get_account_expiration(self) -> datetime:
        """Getter for account expire property

        Returns:
            datetime: The expiration date of the account as a datetime object, or a fixed year 9999 if it does not have an expiration.
        """
        return self.entry.get("accountExpires", datetime(9999, 12, 31))

    def get_last_logon(self) -> datetime:
        """Getter for account last logon datetime

        Returns:
            datetime: The timestamp of the last logon as a datetime object.
        """
        return self.entry.get("lastLogonTimestamp")

    def get_last_logon_days(self) -> int:
        """Getter for account last logon in days

        Returns:
            int: The difference in days between the current date and the last logon date.
        """
        return days_diff(self.get_last_logon())

    def get_pwd_last_set(self) -> datetime:
        """Getter for account password last set date

        Returns:
            datetime: The timestamp of when the password was last set as a datetime object.
        """
        return self.entry.get("pwdLastSet")

    def get_pwd_last_set_days(self) -> int:
        """Getter for account password last set in days

        Returns:
            int: The difference in days between the current date and the date when the password was last set.
        """
        return days_diff(self.get_pwd_last_set())

    def get_account_flags(self) -> List[str]:
        """Getter to retrieve account flags

        Returns:
            List[str]: A list of strings representing the account flags.
        """
        return self.account_flags

    def does_account_expires(self) -> bool:
        """Checks whether the account expires

        Returns:
            bool: True if the account does not expire (not year 9999), False otherwise.
        """
        return not self.get_account_expiration().year == 9999

    def does_pwd_expires(self) -> bool:
        """Getter to check if the account's password expires

        Returns:
            bool: True if the password is set to expire, False otherwise.
        """
        return self.pwd_expires

    def is_pwd_expired(self) -> bool:
        """Getter to check if account password is expired

        Returns:
            bool: True if the password has expired, False otherwise.
        """
        return self.pwd_expired

    def to_dict(self) -> Dict:
        """Converts the current instance into a dict

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
            "account_flags": "-".join(self.account_flags),
        }
