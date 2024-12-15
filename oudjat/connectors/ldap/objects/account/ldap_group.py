from typing import List, Dict

from .. import LDAPObject
from . import LDAPAccount

class LDAPGroup(LDAPObject):
  """ A class to handle LDAP group objects """
  
  # ****************************************************************
    # Attributes & Constructors

  def __init__(self, ldap_entry: LDAPEntry):
    """ Constructor """

    super().__init__(ldap_entry=ldap_entry)

    

  # ****************************************************************
  # Methods
