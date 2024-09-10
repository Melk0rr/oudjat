from __future__ import annotations

import re
from typing import List

import oudjat.connectors.ldap
from oudjat.connectors.ldap.objects import LDAPEntry
from oudjat.connectors.ldap.objects.gpo import MS_GPPREF

UUID_REG = r'(?:\{{0,1}(?:[0-9a-fA-F]){8}-(?:[0-9a-fA-F]){4}-(?:[0-9a-fA-F]){4}-(?:[0-9a-fA-F]){4}-(?:[0-9a-fA-F]){12}\}{0,1})'

class LDAPGroupPolicyObject:
  """ A class to manipulate Group Policy Objects """
  
  # ****************************************************************
  # Attributes & Constructors
  def __init__(self, ldap_entry: LDAPEntry):
    """ Constructor """
    if "groupPolicyContainer" not in ldap_entry.attr().get("objectClass"):
      raise ValueError("Invalid LDAPEntry provided. Please provide a groupPolicyContainer type entry")

    self.name = ldap_entry.attr()["name"]
    self.displayName = ldap_entry.attr()["displayName"]
    
    self.scope = None
    self.scope_property = None
    
    try:
      if len(ldap_entry.attr().get("gPCUserExtensionNames", [])) > 0:
        self.scope = "user"
        self.scope_property = "gPCUserExtensionNames"

      else:
        self.scope = "machine"
        self.scope_property = "gPMachineExtensionNames"

    except Exception as e:
      raise(f"LDAPGPO::Error while trying to get group policy scope\n{e}")

    self.guids = re.findall(UUID_REG, ldap_entry.attr()[self.scope_property])
    self.infos = [ MS_GPPREF[guid] for guid in self.guids ]
    
  # ****************************************************************
  # Methods
  
  def get_guids(self) -> List[str]:
    """ Getter for policy GUIDs """
    return self.guids

  def get_infos(self) -> List[str]:
    """ Getter for policy infos """
    return self.infos
  
  def get_linked_objects(
    self,
    ldap_connector: oudjat.connectors.ldap.LDAPConnector,
    ou: str = "*"
  ) -> List[LDAPEntry]:
    """ Gets the gpo linked objects """
    search_filter = f"(&(gPLink={self.name})(name={ou}))"
    
    linked_entries = ldap_connector.search(
      search_type="DEFAULT",
      search_filter=search_filter
    )

    return linked_entries
