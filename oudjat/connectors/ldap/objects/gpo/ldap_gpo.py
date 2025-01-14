import re
from enum import Enum
from typing import List, Dict, Union

from oudjat.connectors.ldap.objects.definitions import UUID_REG
from oudjat.connectors.ldap.objects import LDAPEntry, LDAPObject, LDAPObjectType

from . import MS_GPPREF

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

    if LDAPObjectType.GPO.value["objectClass"] not in self.entry.get("objectClass"):
      raise ValueError("Invalid LDAPEntry provided. Please provide a groupPolicyContainer type entry")

    self.display_name = self.entry.get("displayName")
    
    self.scope = None
    self.state = None
    
    wql = self.entry.get("gPCWQLFilter", None)

    if wql is not None:
      self.state = LDAPGPOState(int(wql.split(';')[-1][0]))
    
    try:
      if self.entry.get(LDAPGPOScope.USER.value) is not None:
        self.scope = LDAPGPOScope.USER

      else:
        self.scope = LDAPGPOScope.MACHINE

    except Exception as e:
      raise(f"LDAPGPO::Error while trying to get group policy scope\n{e}")

    guids = re.findall(UUID_REG, self.entry.get(self.scope.value))
    self.infos = { guid: MS_GPPREF[guid] for guid in guids }

  # ****************************************************************
  # Methods
  
  def get_display_name(self) -> str:
    """ Getter for GPO display name """
    return self.display_name

  def get_infos(self) -> List[str]:
    """ Getter for policy GUIDs """
    return self.infos

  def get_linked_objects(
    self,
    ldap_connector: "LDAPConnector",
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

  def to_dict(self) -> Dict:
    """ Converts the current instance into a dict """
    base_dict = super().to_dict()
    
    return {
      **base_dict,
      "displayName": self.display_name,
      "scope": self.scope.name,
      "state": self.state.name,
      "infos": " - ".join(self.infos.values())
    }

  # ****************************************************************
  # Static methods
