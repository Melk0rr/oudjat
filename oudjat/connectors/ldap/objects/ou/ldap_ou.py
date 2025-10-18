"""Main module to handle LDAP Organizational Unit stuff."""

import re
from typing import TYPE_CHECKING, Any, override

from oudjat.utils.types import StrType

from ..definitions import UUID_REG
from ..ldap_object_types import LDAPObjectType

if TYPE_CHECKING:
    from ..ldap_entry import LDAPEntry
    from ..ldap_object import LDAPCapabilities, LDAPObject


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
            capabilities (LDAPCapabilities): LDAP capabilities which provide ways for an LDAP object to interact with an LDAP server through an LDAPConnector
        """

        super().__init__(ldap_entry, capabilities)

        self.objects: dict[str, "LDAPObject"] = {}

    # ****************************************************************
    # Methods

    def get_gplink(self) -> str:
        """
        Return the gpLink property of the OU.

        Returns:
            str : gpLink attribute containing links to group policy objects
        """

        return self.entry.get("gPLink")

    def fetch_objects(self, recursive: bool = False) -> None:
        """
        Return the objects contained in the current OU.

        Args:
            recursive (bool): Whether to retrieve objects recursively or not

        Returns:
            list[LDAPObject] : entries of the objects contained in the OU
        """

        search_args: dict[str, Any] = {"search_base": self.get_dn()}
        entries = self.capabilities.ldap_search(attributes="*", **search_args)

        for entry in entries:
            LDAPObjectCls = self.capabilities.ldap_python_cls(
                LDAPObjectType.from_object_cls(entry).name
            )
            new_object = LDAPObjectCls(entry, self.capabilities)

            if isinstance(new_object, "LDAPOrganizationalUnit") and recursive:
                new_object.fetch_objects(recursive)

            self.objects[entry.id] = new_object

    def get_sub_ous(self, recursive: bool = False) -> list["LDAPOrganizationalUnit"]:
        """
        Return only sub OUs from the ou objects.

        Args:
            recursive (bool): Whether to retrieve objects recursively or not

        Returns:
            list[LDAPEntry]: list of sub OUs
        """

        if len(self.objects.keys()) == 0:
            self.fetch_objects(recursive)

        return [obj for obj in self.objects.values() if isinstance(obj, "LDAPOrganizationalUnit")]

    def get_object_per_cls(self, object_cls: StrType | None) -> list["LDAPObject"]:
        """
        Return the current OU objects if they match the provided classes.

        Args:
            object_cls (StrType | None): Object classes the method should return

        Returns:
            list[LDAPObject]: A list of LDAPObject instances matching the provided classes
        """

        if len(self.objects.values()) == 0:
            self.fetch_objects()

        if object_cls is None:
            return list(self.objects.values())

        if not isinstance(object_cls, list):
            object_cls = [object_cls]

        return [obj for obj in self.objects.values() if set(obj.entry.object_cls) & set(object_cls)]

    def get_gpo_from_gplink(self) -> list["LDAPObject"]:
        """
        Extract the GPO references (UUIDs) present in the current OU gpLink.

        It then uses it to retrieve corresponding LDAP GPO instances.

        Args:
            ldap_connector (LDAPConnector): the LDAP connector used to retrieve the GPOs

        Returns:
            list[LDAPObject]: a list of LDAPGroupPolicyObject instances based on the UUIDs in thecurrent OU gpLink attribute
        """

        gpo_refs = re.findall(UUID_REG, self.get_gplink())
        if len(gpo_refs) == 0:
            return []

        gplink_filter = (
            f"(|{''.join([f'(name={link})' for link in gpo_refs])})"
            if len(gpo_refs) > 1
            else f"(name={gpo_refs[0]})"
        )

        gpo_entries = self.capabilities.ldap_search(
            search_type="GPO",
            search_filter=f"(displayName=*){gplink_filter}",
        )

        LDAPGPOType = self.capabilities.ldap_python_cls("GPO")
        def map_gpo(entry: "LDAPEntry"):
            return LDAPGPOType(entry, self.capabilities)

        return list(map(map_gpo, gpo_entries))

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            dict: A dictionary containing the attributes of the LDAP ou in a structured format
        """

        return {**super().to_dict(), "gpLink": self.get_gplink()}
