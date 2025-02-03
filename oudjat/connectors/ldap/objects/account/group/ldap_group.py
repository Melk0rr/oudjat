from typing import Dict, List

from oudjat.connectors.ldap.objects import LDAPObject
from oudjat.model.assets.group import Group

from . import LDAPGroupType


class LDAPGroup(LDAPObject, Group):
    """A class to handle LDAP group objects"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, ldap_entry: "LDAPEntry"):  # noqa: F821
        """Constructor"""

        super().__init__(ldap_entry=ldap_entry)

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
        return self.entry.get("member")

    def get_members(
        self,
        ldap_connector: "LDAPConnector",  # noqa: F821
        recursive: bool = False,
    ) -> List[LDAPObject]:
        """Retreives the group members"""

        for ref in self.get_member_refs():
            # Search for the ref in LDAP server
            ref_search = ldap_connector.search(search_filter=f"(distinguishedName={ref})")

            if len(ref_search) > 0:
                ref_search = ref_search[0]
                obj_class = ref_search.get("objectClass")

                new_member = None

                if self.entry.get_type() == "GROUP":
                    new_member = LDAPGroup(ldap_entry=ref_search)

                    if recursive:
                        new_member.get_members()

    def to_dict(self) -> Dict:
        """Converts the current instance into a dictionary"""
        return {**super().to_dict(), "group_type": self.get_group_type().name}
