from typing import List, Dict

from oudjat.model.assets.group import Group
from oudjat.connectors.ldap.objects import LDAPObject, LDAPEntry

from . import LDAPGroupType

class LDAPGroup(LDAPObject, Group):
  """ A class to handle LDAP group objects """
  
  # ****************************************************************
    # Attributes & Constructors

  def __init__(self, ldap_entry: LDAPEntry):
    """ Constructor """

    super().__init__(ldap_entry=ldap_entry)
    
  # ****************************************************************
  # Methods
  
  def get_group_type_raw(self) -> int:
    """ Getter for group type raw value """
    return self.entry.get("groupType")
  
  def get_group_type(self) -> LDAPGroupType:
    """ Get the group type based on raw value """
    return LDAPGroupType(self.get_group_type_raw())

  def get_member_refs(self) -> List[str]:
    """ Getter for member refs """
    return self.entry.get("members")
    
  # TODO : method to use ldap connector to get member ldap objects
  
  def to_dict(self) -> Dict:
    """ Converts the current instance into a dictionary """
    return {
      **super().to_dict(),
      "group_type": self.get_group_type().name
    }
