from typing import TYPE_CHECKING, Dict, List, Union

from oudjat.model import GenericIdentifiable

from .asset_type import AssetType

if TYPE_CHECKING:
    from ..organization.location import Location


# TODO: better asset description
class Asset(GenericIdentifiable):
    """Generic asset class to be inherited by all model asset types"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        asset_id: Union[int, str],
        name: str,
        asset_type: AssetType,
        label: str = None,
        description: str = None,
        location: Union["Location", List["Location"]] = None,
    ) -> None:
        """
        Constructor for the Asset class.

        Initializes an instance of the Asset class with the provided id, name, asset type, label, and description.
        Also initializes the location attribute as an empty list and sets the given locations using the set_location method.

        Args:
            id (Union[int, str])                                    : The unique identifier for the asset.
            name (str)                                              : The name of the asset.
            asset_type (AssetType)                                  : The type of the asset.
            label (str, optional)                                   : A short description or label for the asset. Defaults to None.
            description (str, optional)                             : A detailed description of the asset. Defaults to None.
            location (Union["Location", List["Location"]], optional): The location(s) where the asset is situated. Defaults to None.
        """

        super().__init__(gid=asset_id, name=name, label=label, description=description)

        self.location = []
        self.set_location(location)

        self.asset_type = asset_type
        self.location = location

    # ****************************************************************
    # Methods

    def get_location(self) -> Union["Location", List["Location"]]:
        """
        Getter for the asset location.

        Returns:
            Union["Location", List["Location"]]: The location(s) of the asset.
        """
        return self.location

    def get_asset_type(self) -> AssetType:
        """Getter for asset type.

        Returns:
            AssetType: The type of the asset.
        """
        return self.asset_type

    def set_location(self, location: Union["Location", List["Location"]]) -> None:
        """
        Setter for asset location.

        Sets the location of the asset to the provided location(s). If a single location is provided, it wraps it in a list.
        Ensures that only instances of Location are added to the asset's locations.

        Args:
            location (Union["Location", List["Location"]]): The location(s) to set for the asset.
        """
        if not isinstance(location, list):
            location = [location]

        new_location = []

        for loc in location:
            if type(loc).__name__ == "Location":
                new_location.append(loc)

        self.location = new_location

    def to_dict(self) -> Dict:
        """Converts current asset into a dict.

        Returns:
            Dict: A dictionary representation of the Asset object including its id, name, label, description, asset type, and location.
        """
        return {
            **super().to_dict(),
            "asset_type": self.asset_type.name,
            "location": self.location,
        }
