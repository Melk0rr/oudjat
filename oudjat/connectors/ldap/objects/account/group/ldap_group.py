"""Main module of the LDAP group package that implement LDAP group object manipulations tools."""

from typing import TYPE_CHECKING, Any, override

from ldap3.utils.conv import escape_filter_chars

from oudjat.assets.group import Group
from oudjat.connectors.ldap.objects.ldap_object_types import LDAPObjectType

from .ldap_group_types import LDAPGroupType

if TYPE_CHECKING:
    from ...ldap_entry import LDAPEntry
    from ...ldap_object import LDAPCapabilities, LDAPObject


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

        self.group: "Group[LDAPObject]" = Group[LDAPObject](
            group_id=self.entry.get("objectGUID"),
            name=self.entry.get("name"),
            label=self.entry.dn,
            description=self.entry.get("description"),
        )

    # ****************************************************************
    # Methods

    @property
    def members(self) -> dict[str, "LDAPObject"]:
        """
        Return the members of the current LDAPGroup.

        Returns:
            dict[str, LDAPObject]: members as a dictionary of LDAPObject instances
        """

        return self.group.members

    def get_group_type_raw(self) -> int:
        """
        Return the group type raw value.

        Returns:
            int: raw group type value
        """

        return self.entry.get("groupType")

    def get_group_type(self) -> "LDAPGroupType":
        """
        Get the group type based on raw value.

        Returns:
            LDAPGroupType: group type based on LDAPGroupType enum
        """

        return LDAPGroupType(self.get_group_type_raw())

    def get_member_refs(self) -> list[str]:
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

        self.group.add_member(member)

    def fetch_members(
        self,
        recursive: bool = False,
    ) -> None:
        """
        Retrieve the group members.

        Args:
            ldap_get_member_func (Callable[..., list[LDAPObject]]): LDAP
            recursive (bool)                                      : Either to retrieve the members recursively or not

        Returns:
            list[LDAPObject]: a list of the group members
        """

        for ref in self.get_member_refs():
            # INFO: Search for the ref in LDAP server
            # TODO: Must implement an LDAPFilter class to handle potential escape characters
            escaped_ref = escape_filter_chars(ref)
            ref_search: list["LDAPEntry"] = self.capabilities.ldap_search(
                search_filter=f"(distinguishedName={escaped_ref})"
            )

            if len(ref_search) > 0:
                search_entry = ref_search[0]
                entry_obj_type = LDAPObjectType.from_object_cls(search_entry)
                LDAPObjectCls = self.capabilities.ldap_obj_opt(entry_obj_type).cls

                new_member = LDAPObjectCls(search_entry, self.capabilities)
                if isinstance(new_member, LDAPGroup) and recursive:
                    new_member.fetch_members(recursive=recursive)

                self.add_member(new_member)

    def get_sub_groups(self, recursive: bool = False) -> list["LDAPGroup"]:
        """
        Return child group of the current group.

        Args:
            ldap_connector (LDAPConnector): LDAP connector instance to use for the request
            recursive (bool)              : Either to retrieve the sub groups recursively or not

        Returns:
            list[LDAPGroup]: a list of sub groups
        """

        if len(self.members.keys()) == 0:
            self.fetch_members(recursive=recursive)

        sub_groups: list["LDAPGroup"] = []
        for member in self.members.values():
            if isinstance(member, LDAPGroup):
                sub_groups.append(member)

                if recursive:
                    sub_groups.extend(member.get_sub_groups(recursive=recursive))

        return sub_groups

    def get_non_group_members(self, recursive: bool = False) -> list["LDAPObject"]:
        """
        Return non group members of the current group.

        Args:
            ldap_connector (LDAPConnector): ldap connector instance to use for the request
            recursive (bool)              : either to retrieve the members recursively or not

        Returns:
            list[LDAPObject]: a list of the members with sub group excluded
        """

        if len(self.members.keys()) == 0:
            self.fetch_members(recursive=recursive)

        members = []
        for member in self.members.values():
            if not isinstance(member, LDAPGroup):
                members.append(member)

            else:
                if recursive:
                    members.extend(member.get_non_group_members(recursive=recursive))

        return members

    def get_members_flat(self) -> list["LDAPObject"]:
        """
        Return a flat list of the current group members.

        Args:
            ldap_connector (LDAPConnector): ldap connector instance to use for the request

        Returns:
            list[LDAPObject]: a list of all the members found recursively but in a flattened list

        """

        if len(self.members.keys()) == 0:
            self.fetch_members(recursive=True)

        members = []
        for member in self.members.values():
            if isinstance(member, LDAPGroup):
                members.extend(member.get_members_flat())

            else:
                members.append(member)

        return members

    def has_member(self, ldap_object: "LDAPObject", extended: bool = False) -> bool:
        """
        Check if the provided object is a member of the current group.

        Args:
            ldap_connector (LDAPConnector): ldap connector instance to use for the request
            ldap_object (LDAPObject)      : object to search
            extended (bool)               : either to check if the object is a member of sub groups

        Returns:
            bool: True if the group contains the given object. False otherwise
        """

        member_ref_list = self.get_members_flat() if extended else self.members.values()
        return ldap_object.id in [m.id for m in member_ref_list]

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            Dict: current instance converted into a dictionary
        """
        return {
            **super().to_dict(),
            **self.group.to_dict(),
            "group_type": self.get_group_type().name,
            "member_names": self.group.member_names,
        }


# TODO: implement an LDAPGroupList to handle lists of LDAPGroup and build membership
