from typing import Dict, List, Union, TYPE_CHECKING

from oudjat.model import GenericIdentifiable

from . import AssetType

if TYPE_CHECKING:
    from ..organization.location import Location

class Asset(GenericIdentifiable):
    """Generic asset class to be inherited by all model asset types"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        id: Union[int, str],
        name: str,
        asset_type: AssetType,
        label: str = None,
        description: str = None,
        location: Union["Location", List["Location"]] = None,  # noqa: F821
    ):
        """Constructor"""

        super().__init__(id=id, name=name, label=label, description=description)

        self.location = []
        self.set_location(location)

        self.asset_type = asset_type
        self.location = location

    # ****************************************************************
    # Methods

    def get_location(self) -> Union["Location", List["Location"]]:
        """Getter for the asset location"""
        return self.location

    def get_asset_type(self) -> AssetType:
        """Getter for asset type"""
        return self.asset_type

    def set_location(self, location: Union["Location", List["Location"]]) -> None:
        """Setter for asset location"""

        if not isinstance(location, list):
            location = [location]

        new_location = []

        for loc in location:
            if type(loc).__name__ == "Location":
                new_location.append(loc)

        self.location = new_location

    def to_dict(self) -> Dict:
        """Converts current asset into a dict"""

        return {
            **super().to_dict(),
            "asset_type": self.asset_type.name,
            "location": self.location,
        }

