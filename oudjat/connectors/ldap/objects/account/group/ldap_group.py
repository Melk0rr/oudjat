"""Main module of the LDAP group package that implement LDAP group object manipulations tools."""

import logging
from typing import TYPE_CHECKING, Any, override

from ldap3.utils.conv import escape_filter_chars

from oudjat.connectors.ldap.ldap_filter import LDAPFilter
from oudjat.connectors.ldap.objects.ldap_object_types import LDAPObjectType
from oudjat.utils.context import Context

from ...ldap_object import LDAPObject
from .ldap_group_types import LDAPGroupType

if TYPE_CHECKING:
    from ...ldap_entry import LDAPEntry
    from ...ldap_object import LDAPCapabilities


class LDAPGroup(LDAPObject):
    """A class to handle LDAP group objects."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        ldap_entry: "LDAPEntry",
        capabilities: "LDAPCapabilities",
        ldap_parent_group: "LDAPGroup | None" = None,
    ) -> None:
        """
        Create a new instance of LDAPGroup.

        Args:
            ldap_entry (LDAPEntry)         : The base dictionary entry
            capabilities (LDAPCapabilities): LDAP capabilities which provide ways for an LDAP object to interact with an LDAP server through an LDAPConnector
            ldap_parent_group (LDAPGroup)  : To optionaly specify the parent group
        """

        super().__init__(ldap_entry, capabilities)
        self.logger: "logging.Logger" = logging.getLogger(__name__)
        self._members: dict[str, "LDAPObject"] = {}

    # ****************************************************************
    # Methods

    @property
    def members(self) -> dict[str, "LDAPObject"]:
        """
        Return the members of the current LDAPGroup.

        Returns:
            dict[str, LDAPObject]: members as a dictionary of LDAPObject instances
        """

        return self._members

    def _group_type_raw(self) -> int:
        """
        Return the group type raw value.

        Returns:
            int: raw group type value
        """

        return self.entry.get("groupType")

    @property
    def group_type(self) -> "LDAPGroupType":
        """
        Get the group type based on raw value.

        Returns:
            LDAPGroupType: group type based on LDAPGroupType enum
        """

        return LDAPGroupType(self._group_type_raw())

    def member_refs(self) -> list[str]:
        """
        Return member refs.

        Returns:
            list[str]: a list of group member refs
        """

        return self.entry.get("member") or []

    def add_member(self, member: "LDAPObject") -> None:
        """
        Add a new member to th current LDAPGroup instance.

        Args:
            member (LDAPObject): member to add
        """

        self._members[member.dn] = member

    def fetch_members(
        self,
        recursive: bool = False,
    ) -> None:
        """
        Retrieve the group members.

        Args:
            recursive (bool): Either to retrieve the members recursively or not
        """

        context = Context()
        self.logger.info(f"{context}::Fetching members of {self.dn}{recursive and ' recursively'}")

        for ref in self.member_refs():
            self.logger.info(f"{context}::Fetching member data for {ref}")

            # INFO: Search for the ref in LDAP server
            escaped_ref = escape_filter_chars(ref)
            ref_search: list["LDAPEntry"] = self.capabilities.ldap_search(
                search_filter=LDAPFilter.dn(escaped_ref)
            )

            if len(ref_search) > 0:
                search_entry = ref_search[0]
                entry_obj_type = LDAPObjectType.from_object_cls(search_entry)
                LDAPObjectCls = self.capabilities.ldap_obj_opt(entry_obj_type).cls

                new_member = LDAPObjectCls(search_entry, capabilities=self.capabilities)
                if isinstance(new_member, LDAPGroup) and recursive:
                    self.logger.debug(f"{context}::Fetching members of sub group {ref}")
                    new_member.fetch_members(recursive=recursive)

                self.logger.debug(f"{context}::Adding new member {ref}")
                self.add_member(new_member)

            else:
                self.logger.warning(f"{context}::Could not find data for {ref}")

    def sub_groups(self, recursive: bool = False) -> dict[str, "LDAPGroup"]:
        """
        Return child group of the current group.

        Args:
            recursive (bool)              : Either to retrieve the sub groups recursively or not

        Returns:
            dict[str, LDAPGroup]: A dictionary of sub groups
        """

        if len(self.members.keys()) == 0:
            self.fetch_members(recursive=recursive)

        self.logger.info(
            f"{Context()}::Fetching sub groups of {self.dn}{recursive and ' recursively'}"
        )

        sub_groups: dict[str, "LDAPGroup"] = {}
        for member in self.members.values():
            if isinstance(member, LDAPGroup):
                sub_groups[f"{member.dn}"] = member

                if recursive:
                    sub_groups.update(member.sub_groups(recursive=recursive))

        return sub_groups

    def non_group_members(self, recursive: bool = False) -> dict[str, "LDAPObject"]:
        """
        Return non group members of the current group.

        Args:
            recursive (bool)              : either to retrieve the members recursively or not

        Returns:
            dict[str, LDAPObject]: A dictionary of the members with sub group excluded
        """

        if len(self.members.keys()) == 0:
            self.fetch_members(recursive=recursive)

        self.logger.info(
            f"{Context()}::Fetching non group members of {self.dn}{recursive and ' recursively'}"
        )

        members = {}
        for member in self.members.values():
            if not isinstance(member, LDAPGroup):
                members[f"{member.dn}"] = member

            else:
                if recursive:
                    members.update(member.non_group_members(recursive=recursive))

        return members

    def members_flat(self) -> dict[str, "LDAPObject"]:
        """
        Return a flat list of the current group members.

        Returns:
            dict[str, LDAPObject]: A dictionary of all the members found recursively but in a flattened dictionary
        """

        if len(self.members.keys()) == 0:
            self.fetch_members(recursive=True)

        self.logger.info(f"{Context()}::Flattening members of {self.dn}")

        members = {}
        for member in self.members.values():
            if isinstance(member, LDAPGroup):
                members.update(member.members_flat())

            else:
                members[f"{member.dn}"] = member

        return members

    def has_member(self, ldap_object: "LDAPObject", extended: bool = False) -> bool:
        """
        Check if the provided object is a member of the current group.

        Args:
            ldap_object (LDAPObject): Object to search
            extended (bool)         : Either to check if the object is a member of sub groups

        Returns:
            bool: True if the group contains the given object. False otherwise
        """

        member_ref_list = self.members_flat().keys() if extended else self.members.keys()
        return ldap_object.dn in member_ref_list

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            dict[str, Any]: The current instance converted into a dictionary
        """

        return {
            **super().to_dict(),
            "members": list(self._members.keys())
        }
