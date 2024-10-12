from oudjat.connectors.ldap.objects import LDAPEntry, LDAPObject
from oudjat.connectors.ldap.objects.account import is_disabled, pwd_expires

class LDAPAccount(LDAPObject):
  def __init__(self, entry: LDAPEntry):
    """ Construcotr """
    
    super().__init__(ldap_entry=entry)
    self.account_control = entry.get("userAccountControl")    
    self.status = "Enabled"
    self.pwd_expires = True
    
    if is_disabled(self.account_control):
      self.status = "Disabled"
      
    if not pwd_expires(self.account_control):
      self.pwd_expires = False
