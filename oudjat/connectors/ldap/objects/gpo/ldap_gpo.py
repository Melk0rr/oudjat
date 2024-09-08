from typing import List

from oudjat.connectors.ldap.ldap_connector import LDAPEntry, LDAPConnector
from oudjat.connectors.ldap.objects.gpo.ms_gppref import MS_GPPREF

class LDAPGPO:
  """ A class to manipulate Group Policy Objects """
  
  # ****************************************************************
  # Attributes & Constructors
  def __init__(self, entry: LDAPEntry):
    """ Constructor """
    if "groupPolicyContainer" not in entry.attr().get("objectClass"):
      raise ValueError("Invalid LDAPEntry provided. Please provide a groupPolicyContainer type entry")

    self.name = entry.attr()["name"]
    self.displayName = entry.attr()["displayName"]
    
    
    

  # ****************************************************************
  # Methods
  
  def get_linked_objects(self, connector: LDAPConnector, ou: str = "*") -> List[LDAPEntry]:
    """ Gets the gpo linked objects """
    search_filter = f"(&(gPLink={self.name})(name={ou}))"
    
    linked_entries = connector.search(
      search_type="DEFAULT",
      search_filter=search_filter
    )

    return linked_entries