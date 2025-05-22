from typing import TYPE_CHECKING, Dict

from oudjat.assets.user import User

from .definitions import MS_ACCOUNT_CTL_PROPERTY
from .ldap_account import LDAPAccount
from .ldap_account_flags import LDAPAccountFlag

if TYPE_CHECKING:
    from ..ldap_entry import LDAPEntry


class LDAPUser(LDAPAccount, User):
    """A class to describe LDAP user objects"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, ldap_entry: "LDAPEntry"):
        """Constructor"""

        super().__init__(ldap_entry=ldap_entry)

        email = self.entry.get("mail", None)
        if email is not None:
            email = email.lower()

        # NOTE: Check additional account control bits (see https://learn.microsoft.com/en-us/windows/win32/adschema/a-msds-user-account-control-computed)
        ms_acc_ctl = self.entry.get(MS_ACCOUNT_CTL_PROPERTY, None)

        if ms_acc_ctl is not None:
            self.enabled = not LDAPAccountFlag.is_disabled(ms_acc_ctl)
            self.pwd_expires = LDAPAccountFlag.pwd_expires(ms_acc_ctl)
            self.pwd_expired = LDAPAccountFlag.pwd_expired(ms_acc_ctl)
            self.pwd_required = LDAPAccountFlag.pwd_required(ms_acc_ctl)
            self.is_locked = LDAPAccountFlag.is_locked(ms_acc_ctl)

            for flag in list(LDAPAccountFlag):
                if LDAPAccountFlag.check_flag(ms_acc_ctl, flag):
                    self.account_flags.add(flag.name)

        User.__init__(
            self,
            user_id=self.uuid,
            name=self.name,
            firstname=self.entry.get("givenName"),
            lastname=self.entry.get("sn"),
            email=email,
            login=self.get_san(),
            description=self.description,
        )

    # ****************************************************************
    # Methods

    def get_employee_id(self) -> str:
        """Getter for the employee id"""
        return self.entry.get("employeeID", None)

    def get_manager(self) -> str:
        """Getter for the user's manager"""
        return self.entry.get("manager", None)

    def is_admin(self) -> bool:
        """Checks if the current user is an admin"""
        is_admin = False
        adm_count = self.entry.get("adminCount", None)

        if adm_count is not None:
            is_admin = adm_count == 1

        return is_admin

    def to_dict(self) -> Dict:
        """Converts the current instance into a dictionary"""
        base_dict = super().to_dict()
        base_dict.pop("san")

        user_dict = User.to_dict(self)

        return {
            **base_dict,
            "employeeID": self.get_employee_id(),
            "manager": self.get_manager(),
            "is_admin": self.is_admin(),
            **user_dict,
        }
