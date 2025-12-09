"""Main module to handle LDAP Organizational Unit stuff."""

import logging
import re
from typing import TYPE_CHECKING, Any, override

from oudjat.utils import Context
from oudjat.utils.types import StrType

from ..definitions import UUID_REG
from ..ldap_object import LDAPObject
from ..ldap_object_types import LDAPObjectType

if TYPE_CHECKING:
    from ..ldap_entry import LDAPEntry
    from ..ldap_object import LDAPCapabilities


class LDAPOrganizationalUnit(LDAPObject):
    """
    A class to handle LDAP Organizational Units.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, ldap_entry: "LDAPEntry", capabilities: "LDAPCapabilities") -> None:
        """
        Initialize a new instance of LDAP OU.

        Args:
            ldap_entry (LDAPEntry)         : ldap entry instance to be used to populate object data
            capabilities (LDAPCapabilities): LDAP capabilities providing ways for an LDAP object to interact with an LDAP server through an LDAPConnector
        """

        super().__init__(ldap_entry, capabilities)

        self._objects: dict[str, "LDAPObject"] = {}
        self.logger: "logging.Logger" = logging.getLogger(__name__)

    # ****************************************************************
    # Methods

    @property
    def gplink(self) -> str:
        """
        Return the gpLink property of the current OU.

        Returns:
            str : gpLink attribute containing links to group policy objects
        """

        return self.entry.get("gPLink")

    @property
    def objects(self) -> dict[str, "LDAPObject"]:
        """
        Return the object contained in the current OU.

        Returns:
            dict[str, LDAPObject]: objects of the current OU represented as a dictionary
        """

        return self._objects

    def fetch_objects(self, recursive: bool = False) -> None:
        """
        Return the objects contained in the current OU.

        Args:
            recursive (bool): Whether to retrieve objects recursively or not
        """

        self.logger.info(f"{Context()}::Fetching object of {self.dn}")

        search_args: dict[str, Any] = {"search_base": self.dn}
        entries = self.capabilities.ldap_search(attributes="*", **search_args)

        for entry in entries:
            obj_type = LDAPObjectType.from_object_cls(entry)
            LDAPObjectCls = self.capabilities.ldap_obj_opt(obj_type).cls
            new_object = LDAPObjectCls(entry, self.capabilities)

            if isinstance(new_object, LDAPOrganizationalUnit) and recursive:
                new_object.fetch_objects(recursive)

            self.objects[entry.dn] = new_object

    def sub_ous(self, recursive: bool = False) -> dict[str, "LDAPOrganizationalUnit"]:
        """
        Return only sub OUs from the ou objects.

        Args:
            recursive (bool): Whether to retrieve objects recursively or not

        Returns:
            dict[str, LDAPOrganizationalUnit]: A dictionary of sub OUs
        """

        if len(self.objects.keys()) == 0:
            self.fetch_objects(recursive)

        self.logger.info(f"{Context()}::Retrieving sub OUs of {self.dn}")

        return {
            obj_id: obj
            for obj_id, obj in self.objects.items()
            if isinstance(obj, "LDAPOrganizationalUnit")
        }

    def object_per_cls(self, object_cls: "StrType | None") -> dict[str, "LDAPObject"]:
        """
        Return the current OU objects if they match the provided classes.

        Args:
            object_cls (StrType | None): Object classes the method should return

        Returns:
            dict[str, LDAPObject]: A dictionary of LDAPObject instances matching the provided classes
        """

        cls_msg = f" {object_cls}" if object_cls else ""
        self.logger.info(f"{Context()}::Retrieving{cls_msg} objects of {self.dn}")

        if len(self.objects.values()) == 0:
            self.fetch_objects()

        if object_cls is None:
            return self.objects

        if not isinstance(object_cls, list):
            object_cls = [object_cls]

        return {
            obj_id: obj
            for obj_id, obj in self.objects.items()
            if set(obj.entry.object_cls) & set(object_cls)
        }

    def gpo_from_gplink(self) -> dict[str, "LDAPObject"]:
        """
        Extract the GPO references (UUIDs) present in the current OU gpLink.

        It then uses it to retrieve corresponding LDAP GPO instances.

        Args:
            ldap_connector (LDAPConnector): the LDAP connector used to retrieve the GPOs

        Returns:
            dict[str, LDAPObject]: a dictionary of LDAPGroupPolicyObject instances based on the UUIDs in the gpLink attribute
        """

        self.logger.info(f"{Context()}::Retrieving GPO applying to {self.dn}")

        gpo_refs = re.findall(UUID_REG, self.gplink)
        if len(gpo_refs) == 0:
            return {}

        gpo_opt = self.capabilities.ldap_obj_opt(LDAPObjectType.GPO)

        return gpo_opt.fetch(name=gpo_refs)

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            dict: A dictionary containing the attributes of the LDAP ou in a structured format
        """

        return {**super().to_dict(), "gpLink": self.gplink, "objects": list(self.objects.keys())}
