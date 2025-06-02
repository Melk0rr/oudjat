"""Main module of the LDAP group package that implement LDAP group object manipulations tools."""

from typing import TYPE_CHECKING, Dict, List

from oudjat.model.assets.group import Group

from ...ldap_object import LDAPObject
from .ldap_group_types import LDAPGroupType

if TYPE_CHECKING:
    from oudjat.connectors.ldap.ldap_connector import LDAPConnector

    from ...ldap_entry import LDAPEntry


class LDAPGroup(LDAPObject, Group):
    """A class to handle LDAP group objects."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, ldap_entry: "LDAPEntry", ldap_parent_group: "LDAPGroup" = None):
        """
        Create a new instance of LDAPGroup.

        Args:
            ldap_entry (LDAPEntry)       : the base dictionary entry
            ldap_parent_group (LDAPGroup): to optionaly specify the parent group
        """

        super().__init__(ldap_entry=ldap_entry)

        Group.__init__(
            self, group_id=self.uuid, name=self.name, label=self.dn, description=self.description
        )

    # ****************************************************************
    # Methods

    def get_group_type_raw(self) -> int:
        """
        Return the group type raw value.

        Returns:
            int: raw group type value
        """

        return self.entry.get("groupType")

    def get_group_type(self) -> LDAPGroupType:
        """
        Get the group type based on raw value.

        Returns:
            LDAPGroupType: group type based on LDAPGroupType enum
        """

        return LDAPGroupType(self.get_group_type_raw())

    def get_member_refs(self) -> List[str]:
        """
        Return member refs.

        Returns:
            List[str]: a list of group member refs
        """

        return self.entry.get("member") or []

    def get_members(
        self,
        ldap_connector: "LDAPConnector",
        recursive: bool = False,
    ) -> List[LDAPObject]:
        """
        Retrieve the group members.

        Args:
            ldap_connector (LDAPConnector): ldap connector instance to use for the request
            recursive (bool)              : either to retrieve the members recursively or not

        Returns:
            List[LDAPObject]: a list of the group members
        """

        if len(self.members.keys()) > 0:
            return super().get_members()

        direct_members = ldap_connector.get_group_members(ldap_group=self, recursive=recursive)

        for member in direct_members:
            self.add_member(member)

        return self.members

    def get_sub_groups(
        self, ldap_connector: "LDAPConnector", recursive: bool = False
    ) -> List["LDAPGroup"]:
        """
        Return child group of the current group.

        Args:
            ldap_connector (LDAPConnector): ldap connector instance to use for the request
            recursive (bool)              : either to retrieve the sub groups recursively or not

        Returns:
            List[LDAPGroup]: a list of sub groups
        """

        if len(self.members.keys()) == 0:
            self.get_members(ldap_connector=ldap_connector, recursive=recursive)

        sub_groups = []
        for member in self.members.values():
            if member.get_type().lower() == "group":
                sub_groups.append(member)

                if recursive:
                    sub_groups.extend(
                        member.get_sub_groups(ldap_connector=ldap_connector, recursive=recursive)
                    )

        return sub_groups

    def get_non_group_members(
        self, ldap_connector: "LDAPConnector", recursive: bool = False
    ) -> List["LDAPObject"]:
        """
        Return non group members of the current group.

        Args:
            ldap_connector (LDAPConnector): ldap connector instance to use for the request
            recursive (bool)              : either to retrieve the members recursively or not

        Returns:
            List[LDAPObject]: a list of the members with sub group excluded
        """

        if len(self.members.keys()) == 0:
            self.get_members(ldap_connector=ldap_connector, recursive=recursive)

        members = []
        for member in self.members.values():
            if not isinstance(member, LDAPGroup):
                members.append(member)

            else:
                if recursive:
                    members.extend(
                        member.get_non_group_members(
                            ldap_connector=ldap_connector, recursive=recursive
                        )
                    )

        return members

    def get_members_flat(self, ldap_connector: "LDAPConnector") -> List["LDAPObject"]:
        """
        Return a flat list of the current group members.

        Args:
            ldap_connector (LDAPConnector): ldap connector instance to use for the request

        Returns:
            List[LDAPObject]: a list of all the members found recursively but in a flattened list

        """

        if len(self.members.keys()) == 0:
            self.get_members(ldap_connector=ldap_connector, recursive=True)

        members = []
        for member in self.members.values():
            if isinstance(member, LDAPGroup):
                members.extend(member.get_members_flat(ldap_connector=ldap_connector))

            else:
                members.append(member)

        return members

    def has_member(
        self, ldap_connector: "LDAPConnector", ldap_object: "LDAPObject", extended: bool = False
    ) -> bool:
        """
        Check if the provided object is a member of the current group.

        Args:
            ldap_connector (LDAPConnector): ldap connector instance to use for the request
            ldap_object (LDAPObject)      : object to search
            extended (bool)               : either to check if the object is a member of sub groups

        Returns:
            bool: True if the group contains the given object. False otherwise
        """

        return ldap_connector.is_object_member_of(
            ldap_object=ldap_object, ldap_group=self, extended=extended
        )

    def to_dict(self) -> Dict:
        """
        Convert the current instance into a dictionary.

        Returns:
            Dict: current instance converted into a dictionary
        """
        return {
            **super().to_dict(),
            "group_type": self.get_group_type().name,
            "member_names": self.get_member_names(),
        }


# TODO: implement an LDAPGroupList to handle lists of LDAPGroup and build membership
