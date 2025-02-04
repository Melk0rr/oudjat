from typing import Dict, Union

from . import Asset


class GroupMemberList(dict):
    """Dict override to handle member list"""


class Group(Asset):
    """A class to handle groups of assets"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        id: Union[int, str],
        name: str,
        label: str = None,
        description: str = None,
    ):
        """Constructor"""

        super().__init__(id=id, name=name, label=label, description=description)

        self.members = GroupMemberList()

    # ****************************************************************
    # Methods
    def get_members(self) -> Dict[Asset]:
        """Returns members of the group"""
        return self.members

    def add_member(self, member: Asset) -> None:
        """Adds a new member to the member list"""
        if isinstance(member, Asset):
            self.members[member.get_id()] = member

    def clear_members(self) -> None:
        """Clears the members of the group"""
        for member in self.member.keys():
            del self.members[member]

    def __str__(self) -> str:
        """Converts the current instance into a string"""
        return f"{self.name}"

