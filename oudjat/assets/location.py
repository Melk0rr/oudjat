"""A module that defines the notion of location."""

from ..assets import Asset, AssetType
from ..assets.network.subnet import Subnet
from .generic_identifiable import GenericIdentifiable


class Location(GenericIdentifiable):
    """A class to describe generic location with subnets, assets, users."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        location_id: int | str,
        name: str,
        description: str | None = None,
        city: str | None = None,
        label: str | None = None,
        subnet: Subnet | dict[int | str, Subnet] | None = None,
    ) -> None:
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

        self._assets: dict[str, dict[int | str, Asset]] = {}
        self._subnet: dict[int | str, Subnet] = {}

        if subnet is not None:
            if not isinstance(subnet, dict):
                self.add_subnet(subnet)

            else:
                self.subnet = subnet

    # ****************************************************************
    # Methods

    @property
    def subnet(self, subnet: str | None = None) -> dict[int | str, Subnet]:
        """
        Return the list of subnets associated with the current location.

        Retrieves the subnet by name. If no specific subnet is provided, returns all subnets as a dictionary.

        Args:
            subnet (str, optional): The name of the subnet to retrieve. Defaults to None.

        Returns:
            Subnet: The subnet instance associated with the given name or all subnets if none specified.
        """

        if subnet is None:
            return self._subnet

        if subnet not in self._subnet.keys():
            raise ValueError(
                f"{__class__.__name__}.get_custom_attr::{subnet} is not a subnet of {self._id}"
            )

        return {subnet: self._subnet[subnet]}

    @subnet.setter
    def subnet(self, new_subnets: dict[int | str, Subnet]) -> None:
        """
         Set the subnets related to the current location.

        Args:
            new_subnets (dict[str, Subnet]): a dictionary of subnet instances
        """

        self._subnet = new_subnets

    def add_subnet(self, subnet: Subnet) -> None:
        """
        Add a new subnet to the location.

        Args:
            subnet (Subnet): The subnet instance to be added to the location.

        Raises:
            ValueError: If an invalid subnet is provided.
        """

        self._subnet[str(subnet)] = subnet

    @property
    def assets(self) -> dict[str, dict[int | str, Asset]]:
        """
        Return the assets currently associated with this location.

        Returns:
            dict[int | str, Asset]: location assets represented as a dictionary
        """

        return self._assets

    @assets.setter
    def assets(self, new_assets: dict[str, dict[int | str, Asset]]) -> None:
        """
        Set the assets associated with the current location.

        Args:
            new_assets (dict[int | str, Asset]): a dictionary of assets to associate with the current location
        """

        for at_name, at_assets in new_assets.items():
            if at_name.upper() not in AssetType._member_names_:
                raise ValueError(
                    f"{__class__.__name__}.@assets.setter::Invalid asset type provided {at_name}"
                )

            self._assets[at_name] = at_assets

    def get_asset(self, asset_type: AssetType, asset_id: int | str) -> Asset:
        """
        Look for an asset based on asset type and id.

        Args:
            asset_type (AssetType): The type of the asset to search for.
            asset_id (int | str)  : The identifier of the asset to search for.

        Returns:
            Asset: The found asset or None if not found.
        """

        return self.assets[asset_type.name][asset_id]

    def get_asset_per_type(self, asset_type: AssetType) -> dict[int | str, Asset] | None:
        """
        Return a dictionary of assets for the given type.

        Args:
            asset_type (AssetType): The type of assets to retrieve.

        Returns:
            Dict: A dictionary of assets filtered by the specified type or None if no assets found.
        """

        return self._assets.get(asset_type.name, None)

    def add_asset(self, asset: Asset) -> None:
        """
        Add a new asset to the current location.

        Args:
            asset (Asset)         : The asset instance to be added.
            asset_type (AssetType): The type of the asset to which the provided asset belongs.

        Raises:
            KeyError: If the asset type does not exist in the assets dictionary.
        """

        if asset.asset_type.name not in self.assets.keys():
            self.assets[asset.asset_type.name] = {}

        if asset.id not in self.assets[asset.asset_type.name].keys():
            self.assets[asset.asset_type.name][asset.id] = asset

    def is_ip_in_subnet(self, ip: str, subnet: str | None = None) -> bool:
        """
        Check if the provided ip is in one of the location subnet.

        The function will check the ip against all of the location's subnets if no specific subnet is provided.

        Args:
            ip (str)              : The IP address to check against the subnets.
            subnet (str, optional): The specific subnet name to check against. Defaults to None.

        Returns:
            bool: True if the IP is within the specified subnet or any subnet if none is specified, False otherwise.
        """

        if len(self._subnet.keys()) == 0 or subnet not in self._subnet.keys():
            return False

        if subnet is not None:
            return self._subnet[f"{subnet}"].contains(ip)

        return any([net.contains(ip) for net in self._subnet.values()])
