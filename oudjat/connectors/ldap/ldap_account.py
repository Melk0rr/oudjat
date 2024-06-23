from oudjat.connectors.ldap.ldap_account_flags import LDAPAccountFlags, is_disabled, pwd_expires
from oudjat.connectors.ldap.ldap_connector import LDAPEntry

class LDAPAccount:
  def __init__(self, entry: LDAPEntry):
    """ Construcotr """

    self.account_control = entry.get("userAccountControl")    
    self.status = "Enabled"
    self.pwd_expires = True
    
    if is_disabled(self.account_control):
      self.status = "Disabled"
      
    if not pwd_expires(self.account_control):
      self.pwd_expires = False
