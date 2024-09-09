from typing import List

import oudjat.connectors.ldap.ldap_connector as ldapcon
from oudjat.connectors.ldap.objects.gpo import MS_GPPREF

class LDAPGroupPolicyObject:
  """ A class to manipulate Group Policy Objects """
  
  # ****************************************************************
  # Attributes & Constructors
  def __init__(self, ldap_entry: ldapcon.LDAPEntry):
    """ Constructor """
    if "groupPolicyContainer" not in entry.attr().get("objectClass"):
      raise ValueError("Invalid LDAPEntry provided. Please provide a groupPolicyContainer type entry")

    self.name = entry.attr()["name"]
    self.displayName = entry.attr()["displayName"]
    
    self.scope = None
    self.scope_property = None
    
    try:
      if len(entry.attr().get("gPCUserExtensionNames", [])) > 0:
        self.scope = "user"
        self.scope_property = "gPCUserExtensionNames"

      else:
        self.scope = "machine"
        self.scope_property = "gPMachineExtensionNames"

    except Exception as e:
      raise(f"LDAPGPO::Error while trying to get group policy scope\n{e}")

    self.guids = entry.attr()[self.scope_property]
    self.infos = [ MS_GPPREF[guid] for guid in self.guids ]
    
  # ****************************************************************
  # Methods
  
  def get_guids(self) -> List[str]:
    """ Getter for policy GUIDs """
    return self.guids

  def get_infos(self) -> List[str]:
    """ Getter for policy infos """
    return self.infos
  
  def get_linked_objects(self, ldap_connector: ldapcon.LDAPConnector, ou: str = "*") -> List[LDAPEntry]:
    """ Gets the gpo linked objects """
    search_filter = f"(&(gPLink={self.name})(name={ou}))"
    
    linked_entries = ldap_connector.search(
      search_type="DEFAULT",
      search_filter=search_filter
    )

    return linked_entries
