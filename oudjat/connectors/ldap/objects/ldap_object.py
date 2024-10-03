from typing import List

from oudjat.connectors.ldap.objects import LDAPEntry

class LDAPObject:
  """ Generic LDAP object """

  # ****************************************************************
  # Attributes & Constructors
  def __init__(self, ldap_entry: LDAPEntry):
    """ Constructor """
    
    self.entry = ldap_entry.attr()