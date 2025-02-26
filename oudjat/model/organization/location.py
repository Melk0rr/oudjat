from typing import Dict, Union

from oudjat.model import GenericIdentifiable

from ..assets import Asset, AssetType
from ..assets.network.subnet import Subnet


class Location(GenericIdentifiable):
    """A class to describe generic location with subnets, assets, users"""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        id: Union[int, str],
        name: str,
        description: str = None,
        city: str = None,
        label: str = None,
        subnet: Union[Subnet, Dict[str, Subnet]] = None,
    ):
        """Constructor"""
        super().__init__(id=id, name=name, label=label, description=description)

        self.assets = {}
        self.subnet: Dict[str, Subnet] = {}

        if subnet is not None:
            if not isinstance(subnet, Dict):
                self.add_subnet(subnet)

            else:
                self.subnet.update(subnet)

    # ****************************************************************
    # Methods

    def get_subnet(self) -> Subnet:
        """Getter for the location subnet"""
        return self.subnet

    def add_subnet(self, subnet: Subnet) -> None:
        """Adds a new subnet to the location"""

        if not isinstance(subnet, Subnet):
            raise ValueError("Location.add_subnet::Invalid subnet provided")

        self.subnet[f"{subnet}"] = subnet

    def get_asset(self, asset_type: AssetType, asset_id: Union[int, str]) -> Asset:
        """Looks for an asset based on asset type and id"""
        return self.assets.get(asset_type.name, {}).get(asset_id, None)

    def get_asset_per_type(self, asset_type: AssetType) -> Dict:
        """Returns a dictionary of assets for the given type"""

        if asset_type.name not in self.assets.keys():
            return None

        return self.assets[asset_type.name]

    def add_asset(self, asset: Asset, asset_type: AssetType) -> None:
        """Adds a new asset to the current location"""

        if asset_type.name not in self.assets.keys():
            self.assets[asset_type.name] = {}

        if asset.get_id() not in self.assets.keys():
            self.assets[asset_type.name][asset.get_id()] = asset

    def is_ip_in_subnet(self, ip: str, subnet: str = None) -> bool:
        """Checks if the provided computer is in the location subnet"""
        if self.subnet is None or (subnet is not None and subnet not in self.subnet.keys()):
            return False

        return (
            self.subnet[f"{subnet}"].contains(ip)
            if subnet is not None
            else any([ net.contains(ip) for net in self.subnet.values() ])
        )
