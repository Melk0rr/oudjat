from datetime import datetime
from typing import Dict, List

from oudjat.utils import date_format_from_flag, DATE_TIME_FLAGS, days_diff
from oudjat.connectors.ldap.objects import LDAPEntry, LDAPObject
from oudjat.connectors.ldap.objects.account import LDAPAccountFlag, check_account_flag, is_disabled, pwd_expires, pwd_expired

MS_ACCOUNT_CTL_PROPERTY = "msDS-User-Account-Control-Computed"

def acc_date_str(date: datetime) -> str:
  """ Converts an account date into a string """
  return date.strftime(date_format_from_flag(DATE_TIME_FLAGS))

class LDAPAccount(LDAPObject):
  """ A class to describe generic LDAP account objects """

  # ****************************************************************
    # Attributes & Constructors

  def __init__(self, ldap_entry: LDAPEntry):
    """ Construcotr """
    
    super().__init__(ldap_entry=ldap_entry)
    self.san = self.entry.get("sAMAccountName")

    self.last_logon = self.entry.get("lastLogonTimestamp")
    self.pwd_last_set = self.entry.get("pwdLastSet")

    self.account_control = self.entry.get("userAccountControl")
    ms_acc_ctl = self.entry.get(MS_ACCOUNT_CTL_PROPERTY, None)

    self.enabled = True
    self.pwd_expires = False
    self.pwd_expired = False
    self.account_flags = []

    if self.account_control is not None:
      self.enabled = not is_disabled(self.account_control)
      self.pwd_expires = pwd_expires(self.account_control)
      self.pwd_expired = pwd_expired(self.account_control)

      self.account_flags = [
        f.name for f in LDAPAccountFlag 
        if check_account_flag(self.account_control, f) or 
          (ms_acc_ctl is not None and check_account_flag(ms_acc_ctl, f))
      ]

    else:
      self.followup_flags.append("MISSING-USR-ACC-CTL")

  # ****************************************************************
  # Methods

  def get_san(self) -> str:
    """ Getter for account sAMAccountName """
    return self.san
  
  def is_enabled(self) -> bool:
    """ Returns wheither the account is enabled or not """
    return self.enabled

  def get_status(self) -> str:
    """ Getter to retreive account status """
    return "Enabled" if self.enabled else "Disabled"

  def get_last_logon(self) -> datetime:
    """ Getter for account last logon datetime """
    return self.last_logon

  def get_last_logon_days(self) -> int:
    """ Getter for account last logon in days """
    return days_diff(self.last_logon)

  def get_pwd_last_set(self) -> datetime:
    """ Getter for account password last set date """
    return self.pwd_last_set

  def get_pwd_last_set_days(self) -> int:
    """ Getter for account password last set in days """
    return days_diff(self.pwd_last_set)
  
  def get_account_flags(self) -> List[str]:
    """ Getter to retreive account flags """
    return self.account_flags
  
  def does_pwd_expires(self) -> bool:
    """ Getter to check if the account's password expires """
    return self.pwd_expires

  def is_pwd_expired(self) -> bool:
    """ Getter to check if account password is expired """
    return self.pwd_expired
  
  def to_dict(self) -> Dict:
    """ Converts the current instance into a dict """
    base_dict = super().to_dict()
    return {
      **base_dict,
      "san": self.san,
      "status": self.get_status(),
      "pwd_expires": self.pwd_expires,
      "pwd_expired": self.pwd_expired,
      "last_logon": acc_date_str(self.last_logon),
      "last_logon_days": self.get_last_logon_days(),
      "pwd_last_set": acc_date_str(self.pwd_last_set),
      "pwd_last_set_days": self.get_pwd_last_set_days(),
      "account_ctl": self.account_control,
      "account_flags": '-'.join(self.account_flags)
    }