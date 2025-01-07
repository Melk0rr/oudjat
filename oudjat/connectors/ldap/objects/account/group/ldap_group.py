from typing import List, Dict

from oudjat.model.assets.group import Group
from oudjat.connectors.ldap.objects import LDAPObject, LDAPEntry

class LDAPGroup(LDAPObject, Group):
  """ A class to handle LDAP group objects """
  
  # ****************************************************************
    # Attributes & Constructors

  def __init__(self, ldap_entry: LDAPEntry):
    """ Constructor """

    super().__init__(ldap_entry=ldap_entry)
    print(self.entry)
    

  # ****************************************************************
  # Methods

  def get_member_refs(self) -> List[str]:
    """ Getter for member refs """
    return self.entry.get("members")
    
  # TODO : method to use ldap connector to get member ldap objects
