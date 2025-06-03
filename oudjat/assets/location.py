"""A module that defines the notion of location."""

from typing import Dict, Union

from oudjat.model import GenericIdentifiable

from ..assets import Asset, AssetType
from ..assets.network.subnet import Subnet


class Location(GenericIdentifiable):
    """A class to describe generic location with subnets, assets, users."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        location_id: Union[int, str],
        name: str,
        description: str = None,
        city: str = None,
        label: str = None,
        subnet: Union[Subnet, Dict[str, Subnet]] = None,
    ):
        """
        Create a new instance of Location.

        Initializes a new location with an ID, name, optional description, city, and label.
        The subnet can be provided as either a single Subnet instance or a dictionary of subnets.

        Args:
            location_id (Union[int, str])                       : A unique identifier for the location.
            name (str)                                          : The name of the location.
            description (str, optional)                         : A description of the location. Defaults to None.
            city (str, optional)                                : The city where the location is situated. Defaults to None.
            label (str, optional)                               : A short label for the location. Defaults to None.
            subnet (Union[Subnet, Dict[str, Subnet]], optional) : The subnet or subnets associated with this location.
        """
        super().__init__(gid=location_id, name=name, label=label, description=description)

        self.assets = {}
        self.subnet: Dict[str, Subnet] = {}

        if subnet is not None:
            if not isinstance(subnet, Dict):
                self.add_subnet(subnet)

            else:
                self.subnet.update(subnet)

    # ****************************************************************
    # Methods

    def get_id(self) -> Union[int, str]:
        """
        Return the current location id.

        Returns:
            Union[int, str]: unique location id
        """

    def get_subnet(self, subnet: str = None) -> Subnet:
        """
        Getter for the location subnet.

        Retrieves the subnet by name. If no specific subnet is provided, returns all subnets as a dictionary.

        Args:
            subnet (str, optional): The name of the subnet to retrieve. Defaults to None.

        Returns:
            Subnet: The subnet instance associated with the given name or all subnets if none specified.
        """

        if self.subnet is None or (subnet is not None and subnet not in self.subnet.keys()):
            return self.subnet

        return self.subnet[subnet]

    def add_subnet(self, subnet: Subnet) -> None:
        """
        Add a new subnet to the location.

        Args:
            subnet (Subnet): The subnet instance to be added to the location.

        Raises:
            ValueError: If an invalid subnet is provided.
        """

        if not isinstance(subnet, Subnet):
            raise ValueError(f"{__class__.__name__}.add_subnet::Invalid subnet provided")

        self.subnet[f"{subnet}"] = subnet

    def get_asset(self, asset_type: AssetType, asset_id: Union[int, str]) -> Asset:
        """
        Look for an asset based on asset type and id.

        Args:
            asset_type (AssetType)      : The type of the asset to search for.
            asset_id (Union[int, str])  : The identifier of the asset to search for.

        Returns:
            Asset: The found asset or None if not found.
        """
        return self.assets.get(asset_type.name, {}).get(asset_id, None)

    def get_asset_per_type(self, asset_type: AssetType) -> Dict:
        """
        Return a dictionary of assets for the given type.

        Args:
            asset_type (AssetType): The type of assets to retrieve.

        Returns:
            Dict: A dictionary of assets filtered by the specified type or None if no assets found.
        """

        if asset_type.name not in self.assets.keys():
            return None

        return self.assets[asset_type.name]

    def add_asset(self, asset: Asset, asset_type: AssetType) -> None:
        """
        Add a new asset to the current location.

        Args:
            asset (Asset)         : The asset instance to be added.
            asset_type (AssetType): The type of the asset to which the provided asset belongs.

        Raises:
            KeyError: If the asset type does not exist in the assets dictionary.
        """

        if asset_type.name not in self.assets.keys():
            self.assets[asset_type.name] = {}

        if asset.get_id() not in self.assets.keys():
            self.assets[asset_type.name][asset.get_id()] = asset

    def is_ip_in_subnet(self, ip: str, subnet: str = None) -> bool:
        """
        Check if the provided computer is in the location subnet.

        Args:
            ip (str)              : The IP address to check against the subnets.
            subnet (str, optional): The specific subnet name to check against. Defaults to None.

        Returns:
            bool: True if the IP is within the specified subnet or any subnet if none is specified, False otherwise.
        """

        if self.subnet is None or (subnet is not None and subnet not in self.subnet.keys()):
            return False

        return (
            self.subnet[f"{subnet}"].contains(ip)
            if subnet is not None
            else any([net.contains(ip) for net in self.subnet.values()])
        )
