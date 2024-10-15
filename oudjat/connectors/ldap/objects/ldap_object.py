from typing import List, Dict
from ldap3.utils.dn import parse_dn

from oudjat.connectors.ldap.objects import LDAPEntry

class LDAPObject:
  """ Generic LDAP object """

  # ****************************************************************
  # Attributes & Constructors
  def __init__(self, ldap_entry: LDAPEntry):
    """ Constructor """
    
    self.entry = ldap_entry.attr()
    self.dn = self.entry.get_dn()
    self.name = self.entry.get("name")
    self.description = self.entry.get("description", "")

    self.object_classes = self.entry.get("objectClass", [])
    
    self.dn_pices = parse_dn(self.dn, escape=True)

  # ****************************************************************
  # Methods

  def is_of_object_class(self, obj_cl: str) -> bool:
    """ Checks if the current object is of given class """
    return obj_cl.lower() in self.object_classes