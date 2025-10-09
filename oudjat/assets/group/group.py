"""A module that describes group of assets."""

from typing import override

from ..asset import Asset
from ..asset_type import AssetType
from ..generic_identifiable import GenericIdentifiable


class GroupMemberList(dict):
    """Dict override to handle member list."""

MemberType = TypeVar("MemberType", bound=GenericIdentifiable)

class Group(Asset, Generic[MemberType]):
    """A class to handle groups of assets."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        group_id: int | str,
        name: str,
        label: str | None = None,
        description: str | None = None,
        **kwargs: Any
    ) -> None:
        """
        Create a new Group of assets.

        Args:
            group_id (Union[int, str]) : The identifier of the group.
            name (str)                 : The name of the group.
            label (str, optional)      : A short text label for the group. Defaults to None.
            description (str, optional): A detailed description of the group. Defaults to None.
            kwargs (Any)               : Any further arguments
        """

        super().__init__(
            asset_id=group_id,
            name=name,
            label=label,
            description=description,
            asset_type=AssetType.GROUP,
            **kwargs,
        )

        self._members: dict[str, MemberType] = {}

    # ****************************************************************
    # Methods

    @property
    def members(self) -> dict[str, MemberType]:
        """
        Return the members of the group.

        Returns:
            Dict[str, Asset]: A dictionary containing all members by their identifier.
        """

        return self.members

    def get_member_names(self) -> list[str]:
        """
        Return the list of member names in the group.

        Returns:
            List[str]: A list of names of all members.
        """

        return [m.get_name() for m in self.members.values()]

    def add_member(self, member: GenericIdentifiable) -> None:
        """
        Add a new member to the group.

        Args:
            member (GenericIdentifiable): The asset to be added as a member.
        """

        self.members[member.id] = member

    def clear_members(self) -> None:
        """
        Clear all members from the group.

        This method deletes all entries in the member list.
        """

        for member_id in list(
            self.members.keys()
        ):  # Using list to avoid RuntimeError during modification
            del self.members[member_id]

    @override
    def __str__(self) -> str:
        """
        Convert the current instance into a string representation.

        Returns:
            str: A string that represents the group's name.
        """

        return f"{self._name}"
