"""A module that defines base Asset properties."""

from abc import ABC
from typing import TYPE_CHECKING, Any, TypedDict, TypeVar, override

from oudjat.control.risk.risk import Risk
from oudjat.core.exceptions import InvalidAssetTypeError
from oudjat.utils import Context, UtilsDict

from .asset_type import AssetType
from .generic_identifiable import GenericIdentifiable

if TYPE_CHECKING:
    from .location import Location

AssetBoundType = TypeVar("AssetBoundType", bound="Asset")

class AssetBaseDict(TypedDict):
    """
    A helper class to properly handle Asset base dictionary attributes.

    Attributes:
        assetType (AssetType)               : The asset type
        location (dict[int | str, Location]): The locations associated with the asset
    """

    assetType: str
    location: dict[str, dict[str, Any]]

class Asset(GenericIdentifiable[AssetBoundType], ABC):
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
            asset_id (int | str)                        : The unique identifier for the asset.
            name (str)                                  : The name of the asset.
            asset_type (AssetType)                      : The type of the asset.
            label (str | None)                          : A short description or label for the asset. Defaults to None.
            description (str | None)                    : A detailed description of the asset. Defaults to None.
            location (Location | list[Location] | None) : The location(s) where the asset is situated. Defaults to None.
            kwargs (Any)                                : Any further arguments
        """

        super().__init__(gid=asset_id, name=name, label=label or "", description=description, **kwargs)

        self._asset_type: "AssetType" = asset_type
        self._location: dict[str, "Location"] = {}

        if location is not None:
            self._set_location_from_instances(location)

        self.risks: dict[str, "Risk"] = {}

    # ****************************************************************
    # Methods

    @property
    def location(self) -> dict[str, "Location"]:
        """The location property."""

        return self._location

    @location.setter
    def location(self, new_location: dict[str, "Location"]) -> None:
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

    def add_location(self, new_location: "Location") -> None:
        """
        Add a new location to the asset.

        Args:
            new_location (Location): New location to bound to the asset
        """

        self._location[f"{new_location.id}"] = new_location

    def _set_location_from_instances(self, new_location: "Location | list[Location]") -> None:
        """
        Setter for asset location.

        Sets the location of the asset to the provided location(s). If a single location is provided, it wraps it in a list.
        Ensures that only instances of Location are added to the asset's locations.

        Args:
            new_location (Location | list[Location]): The location(s) to set for the asset.
        """

        if not isinstance(new_location, list):
            new_location = [new_location]

        self._location = { f"{loc.id}": loc for loc in new_location }

    @override
    def merge(self, other: "AssetBoundType") -> None:

        if other.asset_type is not self.asset_type:
            raise InvalidAssetTypeError(f"{Context()}::Trying to merge two assets of different types")

        super().merge(other)

        self._location = UtilsDict.merge_dictionaries(self._location, other.location)


    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert current asset into a dict.

        Returns:
            dict[str, Any]: A dictionary representation of the Asset object including its id, name, label, description, asset type, and location.
        """

        base_dict: "AssetBaseDict" = {
            "assetType": str(self._asset_type),
            "location": {loc_k: loc.to_dict() for loc_k, loc in self._location.items()},
        }

        return {
            **super().to_dict(),
            **base_dict
        }
