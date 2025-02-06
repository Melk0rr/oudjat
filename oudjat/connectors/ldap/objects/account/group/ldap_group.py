from typing import TYPE_CHECKING, Dict, List

from oudjat.model.assets.group import Group

from ...ldap_object import LDAPObject
from .ldap_group_types import LDAPGroupType

if TYPE_CHECKING:
    from oudjat.connectors.ldap import LDAPConnector
    from ...ldap_entry import LDAPEntry


class LDAPGroup(LDAPObject, Group):
    """A class to handle LDAP group objects"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, ldap_entry: "LDAPEntry", ldap_parent_group: "LDAPGroup" = None):
        """Constructor"""

        super().__init__(ldap_entry=ldap_entry)
        
        Group.__init__(
            self,
            id=self.uuid,
            name=self.name,
            label=self.dn,
            description=self.description
        )

    # ****************************************************************
    # Methods

    def get_group_type_raw(self) -> int:
        """Getter for group type raw value"""
        return self.entry.get("groupType")

    def get_group_type(self) -> LDAPGroupType:
        """Get the group type based on raw value"""
        return LDAPGroupType(self.get_group_type_raw())

    def get_member_refs(self) -> List[str]:
        """Getter for member refs"""
        return self.entry.get("member") or []

    def get_members(
        self,
        ldap_connector: "LDAPConnector",
        recursive: bool = False,
    ) -> List[LDAPObject]:
        """Retreives the group members"""
        if len(self.members.keys()) > 0:
            return super().get_members()

        direct_members = ldap_connector.get_group_members(ldap_group=self, recursive=recursive)

        for member in direct_members:
            self.add_member(member)

        return self.members

    def get_sub_groups(
        self, ldap_connector: "LDAPConnector", recursive: bool = False
    ) -> List["LDAPGroup"]:
        """Returns child group of the current group"""
        if len(self.members.keys()) == 0:
            self.get_members()

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
        """Returns non group members of the current group"""
        if len(self.members.keys()) == 0:
            self.get_members()

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
        """Returns a flat list of the current group members"""
        if len(self.members.keys()) == 0:
            self.get_members()

        members = []
        for member in self.members.values():
            if isinstance(member, LDAPGroup):
                members.extend(member.get_members_flat(ldap_connector=ldap_connector))

            else:
                member.append(member)

        return members

    def is_member(self, ldap_connector: "LDAPConnector", ldap_object: "LDAPObject", extended: bool = False) -> bool:
        """Checks if the provided object is a member of the current group"""
        if len(self.members.keys()) == 0:
            self.get_members()

        member_ref_list = None

        if extended:
            member_ref_list = self.get_members_flat(ldap_connector=ldap_connector)

        else:
            member_ref_list = self.members.values()

        return ldap_object.get_uuid() in [ m.get_id() for m in member_ref_list ]

    def to_dict(self) -> Dict:
        """Converts the current instance into a dictionary"""
        return {
            **super().to_dict(),
            "group_type": self.get_group_type().name,
            "member_names": self.get_member_names(),
        }

# TODO: implement an LDAPGroupList to handle lists of LDAPGroup and build membership
