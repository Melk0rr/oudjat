"""A module to allow Group policy object retrieving and manipulations throug LDAPConnector."""

import logging
import re
from enum import Enum, IntEnum
from typing import TYPE_CHECKING, Any, override

from oudjat.utils import Context
from oudjat.utils.types import StrType

from ...ldap_filter import LDAPFilter
from ..definitions import UUID_REG
from ..ldap_object import LDAPObject
from ..ldap_object_types import LDAPObjectType
from .ms_cse import MS_CSE

if TYPE_CHECKING:
    from ..ldap_entry import LDAPEntry
    from ..ldap_object import LDAPCapabilities


class LDAPGPOScope(Enum):
    """GPO scope enumeration."""

    USER = "gPCUserExtensionNames"
    MACHINE = "gPCMachineExtensionNames"


class LDAPGPOState(IntEnum):
    """GPO state enumeration."""

    NO_FILTER = -1
    ENABLED = 0
    DISABLED = 1
    ENFORCED = 2


class LDAPGroupPolicyObject(LDAPObject):
    """A class to manipulate Group Policy Objects."""

    # ****************************************************************
    # Attributes & Constructors
    def __init__(self, ldap_entry: "LDAPEntry", capabilities: "LDAPCapabilities") -> None:
        """
        Initialize an instance of LDAPGPO.

        This constructor takes an LDAP entry as input and initializes the object with necessary attributes derived from the entry.

        Args:
            ldap_entry (LDAPEntry)         : An LDAP entry representing a group policy object.
            capabilities (LDAPCapabilities): LDAP capabilities which provide ways for an LDAP object to interact with an LDAP server through an LDAPConnector
        """

        super().__init__(ldap_entry, capabilities)
        self.logger: "logging.Logger" = logging.getLogger(__name__)

    # ****************************************************************
    # Methods

    @property
    def display_name(self) -> str:
        """
        Return the display name of the current GPO.

        Returns:
            str: The display name of the group policy object.
        """

        return self.entry.get("displayName")

    @property
    def path(self) -> str:
        """
        Return the GPO path in sysvol.

        Returns:
            str: The sysvol path of the GPO
        """

        return self.entry.get("gPCFileSysPath")

    @property
    def state(self) -> "LDAPGPOState":
        """
        Return the current GPO state.

        Returns:
            LDAPGPOState: The state of the current GPO as an LDAPGPOState element
        """

        wql = self.entry.get("gPCWQLFilter", None)
        if wql is None:
            return LDAPGPOState.NO_FILTER

        return LDAPGPOState(int(wql.split(";")[-1][0]))

    @property
    def scope(self) -> "LDAPGPOScope":
        """
        Return the scope of the current GPO instance.

        Returns:
            LDAPGPOScope: LDAPGPOScope.USER if the appropriate property is present in the GPO entry. Else LDAPGPOScope.MACHINE
        """

        return (
            LDAPGPOScope.USER
            if self.entry.get(LDAPGPOScope.USER.value) is not None
            else LDAPGPOScope.MACHINE
        )

    @property
    def infos(self) -> dict[str, str]:
        """
        Return the GUIDs of the current GPO and teir matching description.

        Returns:
            dict[str, str]: A list of GUIDs associated with the group policy preferences.
        """

        guids: list[str] = re.findall(UUID_REG, self.entry.get(self.scope.value))
        return {guid: MS_CSE[guid] if guid in MS_CSE else "[Unknown CSE GUID]" for guid in guids}

    def linked_objects(
        self,
        attributes: "StrType | None" = None,
        ou: str = "*",
    ) -> dict[str, "LDAPObject"]:
        """
        Get the GPO linked objects.

        This method searches for LDAP entries that are linked to the current group policy object (GPO).

        Args:
            attributes (str | list[str] | None): The attributes to retrieve from the linked LDAP entries.
            ou (str | None)                    : The organizational unit (OU) in which to search for linked objects.

        Returns:
            list["LDAPObject"]: A list of LDAPOrganizationalUnit instances that are linked to the current GPO.
        """

        self.logger.info(f"{Context()}::Retrieving linked object of {self.display_name}")

        obj_opt = self.capabilities.ldap_obj_opt(LDAPObjectType.OU)
        LDAPOUCls = obj_opt.cls

        obj_filter = LDAPFilter(f"(gPLink={f'*{self._name}*'})") & LDAPFilter.name(ou)

        res = {}
        for entry in obj_opt.fetch(search_filter=obj_filter, attributes=attributes):
            res[entry.dn] = LDAPOUCls(entry, capabilities=self.capabilities)

        return res

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dict.

        This method converts the group policy object (GPO) and its related information into a dictionary format for easier serialization or transmission.

        Returns:
            dict[str, Any]: A dictionary containing the GPO's display name, scope, state, and linked GUIDs.
        """

        base_dict = super().to_dict()

        return {
            **base_dict,
            "displayName": self.display_name,
            "scope": self.scope.name,
            "state": self.state.name,
            "path": self.path,
            "infos": self.infos,
            "linkedObjects": list(self.linked_objects().keys()),
        }

    # ****************************************************************
    # Static methods
