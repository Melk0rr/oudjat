from datetime import datetime, timezone
from typing import Dict

from oudjat.connectors.ldap.objects import LDAPEntry, LDAPObject
from oudjat.connectors.ldap.objects.account import LDAPAccountFlag, check_account_flag, is_disabled, pwd_expires, pwd_expired

def days_diff(date: datetime) -> int:
  """ Returns difference between today and a past date """
  diff = -1
  if date is not None:
    diff = datetime.now(timezone.utc) - date
    
  return diff.days

class LDAPAccount(LDAPObject):
  def __init__(self, ldap_entry: LDAPEntry):
    """ Construcotr """

    # ****************************************************************
    # Attributes & Constructors
    
    super().__init__(ldap_entry=ldap_entry)
    self.san = self.entry.get("sAMAccountName")

    self.last_logon = self.entry.get("lastLogonTimestamp")
    self.last_logon_days = days_diff(self.last_logon)

    self.pwd_last_set = self.entry.get("pwdLastSet")
    self.pwd_last_set_days = days_diff(self.pwd_last_set)
    
    self.account_control = self.entry.get("userAccountControl")

    self.status = "Enabled"
    if is_disabled(self.account_control):
      self.status = "Disabled"
      
    self.pwd_expires = False
    if not pwd_expires(self.account_control):
      self.pwd_expires = True

    self.pwd_expired = False
    if pwd_expired(self.account_control):
      self.pwd_expires = True

    self.account_flags = [ f.name for f in LDAPAccountFlag if check_account_flag(self.account_control, f) ]

  # ****************************************************************
  # Methods
  
  def to_dict(self) -> Dict:
    """ Converts the current instance into a dict """
    base_dict = super().to_dict()
    return {
      **base_dict,
      "san": self.san,
      "status": self.status,
      "pwd_expires": self.pwd_expires,
      "pwd_expired": self.pwd_expired,
      "last_logon": self.last_logon,
      "last_logon_days": self.last_logon_days,
      "pwd_last_set": self.pwd_last_set,
      "pwd_last_set_days": self.pwd_last_set_days,
      "account_ctl": self.account_control,
      "account_flags": self.account_flags
    }