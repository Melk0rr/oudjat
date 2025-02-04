from typing import TYPE_CHECKING, Dict, List

from oudjat.model.assets.group import Group

from ...ldap_object import LDAPObject
from . import LDAPGroupType

if TYPE_CHECKING:
    from oudjat.connectors.ldap import LDAPConnector

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
        ldap_connector: "LDAPConnector",
        recursive: bool = False,
    ) -> List[LDAPObject]:
        """Retreives the group members"""
        if len(self.members.keys()) > 0:
            return super().get_members()

        return ldap_connector.get_group_members(ldap_group=self, recursive=recursive)


    def to_dict(self) -> Dict:
        """Converts the current instance into a dictionary"""
        return {**super().to_dict(), "group_type": self.get_group_type().name}
