from __future__ import annotations

import re
from enum import Enum
from typing import List, Dict, Union

import oudjat.connectors.ldap
from oudjat.connectors.ldap.objects import LDAPEntry, LDAPObject

from . import MS_GPPREF

UUID_REG = r'(?:\{{0,1}(?:[0-9a-fA-F]){8}-(?:[0-9a-fA-F]){4}-(?:[0-9a-fA-F]){4}-(?:[0-9a-fA-F]){4}-(?:[0-9a-fA-F]){12}\}{0,1})'

class LDAPGPOScope(Enum):
  """ GPO scope """
  USER = "gPCUserExtensionNames"
  MACHINE = "gPCMachineExtensionNames"

class LDAPGPOState(Enum):
  ENABLED = 0
  DISABLED = 1
  ENFORCED = 2

class LDAPGroupPolicyObject(LDAPObject):
  """ A class to manipulate Group Policy Objects """
  
  # ****************************************************************
  # Attributes & Constructors
  def __init__(self, ldap_entry: LDAPEntry):
    """ Constructor """
    super().__init__(ldap_entry=ldap_entry)

    if "groupPolicyContainer" not in self.entry.get("objectClass"):
      raise ValueError("Invalid LDAPEntry provided. Please provide a groupPolicyContainer type entry")

    self.name = self.entry.get("name")
    self.display_name = self.entry.get("displayName")
    
    self.scope = None
    self.scope_property = None

    self.state = None
    wql = self.entry.get("gPCWQLFilter", None)

    if wql is not None:
      self.state = LDAPGPOState(int(wql.split(';')[-1][0]))
    
    try:
      if len(self.entry.get("gPCUserExtensionNames", [])) > 0:
        self.scope = LDAPGPOScope.USER

      else:
        self.scope = LDAPGPOScope.MACHINE

    except Exception as e:
      raise(f"LDAPGPO::Error while trying to get group policy scope\n{e}")

    self.guids = re.findall(UUID_REG, self.entry.get(self.scope.value))
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
