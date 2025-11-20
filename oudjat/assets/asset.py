"""A module that defines base Asset properties."""

from abc import ABC
from typing import TYPE_CHECKING, Any, override

from .asset_type import AssetType
from .generic_identifiable import GenericIdentifiable

if TYPE_CHECKING:
    from .location import Location


class Asset(GenericIdentifiable, ABC):
    """
    Generic asset class. Must be inherited by asset types.

    This class serves as a base for any asset type may it be equipment hardware or software, users, etc.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        asset_id: int | str,
        name: str,
        asset_type: "AssetType",
        label: str | None = None,
        description: str | None = None,
        location: "Location | list[Location] | None" = None,
        **kwargs: Any,
    ) -> None:
        """
        Create a new instance of Asset.

        Initializes an instance of the Asset class with the provided id, name, asset type, label, and description.
        Also initializes the location attribute as an empty list and sets the given locations using the set_location method.

        Args:
            asset_id (int | str)                              : The unique identifier for the asset.
            name (str)                                        : The name of the asset.
            asset_type (AssetType)                            : The type of the asset.
            label (str | None)                                : A short description or label for the asset. Defaults to None.
            description (str | None)                          : A detailed description of the asset. Defaults to None.
            location (Location | list[Location] | None)       : The location(s) where the asset is situated. Defaults to None.
            kwargs (Any)                                      : Any further arguments
        """

        super().__init__(gid=asset_id, name=name, label=label or "", description=description or "")

        self._asset_type: "AssetType" = asset_type
        self._location: dict[int | str, "Location"] = {}

        if location is not None:
            self.set_location_from_instance(location)

    # ****************************************************************
    # Methods

    @property
    def location(self) -> dict[int | str, "Location"]:
        """The location property."""

        return self._location

    @location.setter
    def location(self, new_location: dict[int | str, "Location"]) -> None:
        """
        Set the location of the current asset.

        Args:
            new_location (Location | list[Location]): new location to associate to the asset
        """

        self._location = new_location

    @property
    def asset_type(self) -> "AssetType":
        """
        Return the asset type of the current object.

        Returns:
            AssetType: asset type associated with the current asset
        """

        return self._asset_type

    def set_location_from_instance(self, new_location: "Location | list[Location]") -> None:
        """
        Setter for asset location.

        Sets the location of the asset to the provided location(s). If a single location is provided, it wraps it in a list.
        Ensures that only instances of Location are added to the asset's locations.

        Args:
            new_location (Location | list[Location]): The location(s) to set for the asset.
        """

        if not isinstance(new_location, list):
            new_location = [new_location]

        self._location = { loc.id: loc for loc in new_location }

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert current asset into a dict.

        Returns:
            dict[str, Any]: A dictionary representation of the Asset object including its id, name, label, description, asset type, and location.
        """
        return {
            **super().to_dict(),
            "asset_type": self.asset_type.name,
            "location": self.location,
        }
