from __future__ import annotations

import re
from typing import List, Dict, Union

import oudjat.connectors.ldap
from oudjat.connectors.ldap.objects import LDAPEntry

from . import MS_GPPREF
from . import LDAPGroupPolicyState

UUID_REG = r'(?:\{{0,1}(?:[0-9a-fA-F]){8}-(?:[0-9a-fA-F]){4}-(?:[0-9a-fA-F]){4}-(?:[0-9a-fA-F]){4}-(?:[0-9a-fA-F]){12}\}{0,1})'

class LDAPGroupPolicyObject:
  """ A class to manipulate Group Policy Objects """
  
  # ****************************************************************
  # Attributes & Constructors
  def __init__(self, ldap_entry: LDAPEntry):
    """ Constructor """
    self.entry = ldap_entry.attr()
    if "groupPolicyContainer" not in self.entry.get("objectClass"):
      raise ValueError("Invalid LDAPEntry provided. Please provide a groupPolicyContainer type entry")

    self.name = self.entry["name"]
    self.displayName = self.entry["displayName"]
    
    self.scope = None
    self.scope_property = None

    self.state = None
    wql = self.entry.get("gPCWQLFilter", None)

    if wql is not None:
      self.state = LDAPGroupPolicyState(int(wql.split(';')[-1][0]))
    
    try:
      if len(self.entry.get("gPCUserExtensionNames", [])) > 0:
        self.scope = "user"
        self.scope_property = "gPCUserExtensionNames"

      else:
        self.scope = "machine"
        self.scope_property = "gPCMachineExtensionNames"

    except Exception as e:
      raise(f"LDAPGPO::Error while trying to get group policy scope\n{e}")

    self.guids = re.findall(UUID_REG, self.entry[self.scope_property])
    self.infos = [ MS_GPPREF[guid] for guid in self.guids ]
    
  # ****************************************************************
  # Methods

  def get_entry(self) -> Dict:
    """ Getter for entry attributes """
    return self.entry

  def get_dn(self) -> str:
    """ Getter for gpo dn """
    return self.entry.get("distinguishedName")
  
  def get_guids(self) -> List[str]:
    """ Getter for policy GUIDs """
    return self.guids

  def get_infos(self) -> List[str]:
    """ Getter for policy infos """
    return self.infos
  
  def get_linked_objects(
    self,
    ldap_connector: oudjat.connectors.ldap.LDAPConnector,
    attributes: Union[str, List[str]] = None,
    ou: str = "*"
  ) -> List[LDAPEntry]:
    """ Gets the gpo linked objects """
    search_filter = f"(gPLink={f"*{self.name}*"})(name={ou})"
    
    linked_entries = ldap_connector.search(
      search_type="OU",
      search_filter=search_filter,
      attributes=attributes
    )

    return linked_entries

  # ****************************************************************
  # Static methods
