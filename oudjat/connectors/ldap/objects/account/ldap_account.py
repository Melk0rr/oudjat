from datetime import datetime

from oudjat.connectors.ldap.objects import LDAPEntry, LDAPObject
from oudjat.connectors.ldap.objects.account import is_disabled, pwd_expires

def days_diff(date: datetime) -> int:
  """ Returns difference between today and a past date """
  diff = -1
  if date is not None:
    diff = datetime.now() - date
    
  return diff

class LDAPAccount(LDAPObject):
  def __init__(self, ldap_entry: LDAPEntry):
    """ Construcotr """

    # ****************************************************************
    # Attributes & Constructors
    
    super().__init__(ldap_entry=ldap_entry)
    self.account_control = self.entry.get("userAccountControl")
    self.san = self.entry.get("sAMAccountName")

    self.last_logon = self.entry.get("lastLogon")
    self.last_logon_days = days_diff(self.last_logon)

    self.pwd_last_set = self.entry.get("pwdLastSet")
    self.pwd_last_set_days = days_diff(self.pwd_last_set)
    
    self.status = "Enabled"
    if is_disabled(self.account_control):
      self.status = "Disabled"
      
    self.pwd_expires = True
    if not pwd_expires(self.account_control):
      self.pwd_expires = False


  # ****************************************************************
  # Methods
  