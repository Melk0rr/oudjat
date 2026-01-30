"""A module that defines the notion of location."""

from typing import Any, override

from oudjat.core.asset_type import AssetType
from oudjat.utils import Context

from ..core.network.subnet import Subnet
from .asset import Asset


class Location(Asset):
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
        subnet: "Subnet | dict[int | str, Subnet] | None" = None,
    ) -> None:
        """
        Create a new instance of Location.

        Initializes a new location with an ID, name, optional description, city, and label.
        The subnet can be provided as either a single Subnet instance or a dictionary of subnets.

        Args:
            location_id (int | str)                         : A unique identifier for the location.
            name (str)                                      : The name of the location.
            description (str | None)                        : A description of the location. Defaults to None.
            city (str | None)                               : The city where the location is situated. Defaults to None.
            label (str | None)                              : A short label for the location. Defaults to None.
            subnet (Subnet | dict[int | str, Subnet] | None): The subnet or subnets associated with this location.
        """

        super().__init__(
            asset_id=location_id,
            name=name,
            label=label,
            description=description,
            asset_type=AssetType.LOCATION,
        )

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
            subnet (str | None): The name of the subnet to retrieve. Defaults to None.

        Returns:
            Subnet: The subnet instance associated with the given name or all subnets if none specified.
        """

        if subnet is None:
            return self._subnet

        if subnet not in self._subnet.keys():
            raise ValueError(f"{Context()}::{subnet} is not a subnet of {self._id}")

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

    def is_ip_in_subnet(self, ip: str, subnet: str | None = None) -> bool:
        """
        Check if the provided ip is in one of the location subnet.

        The function will check the ip against all of the location's subnets if no specific subnet is provided.

        Args:
            ip (str)           : The IP address to check against the subnets.
            subnet (str | None): The specific subnet name to check against. Defaults to None.

        Returns:
            bool: True if the IP is within the specified subnet or any subnet if none is specified, False otherwise.
        """

        if len(self._subnet.keys()) == 0 or subnet not in self._subnet.keys():
            return False

        if subnet is not None:
            return self._subnet[f"{subnet}"].contains(ip)

        return any([net.contains(ip) for net in self._subnet.values()])

    @override
    def __str__(self) -> str:
        """
        Convert the current instance into a string.

        Returns:
            str: String representation of the current instance
        """

        return self._name

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current location into a dictionary.

        Returns:
            dict[str, Any]: A dictionary representation of the current location
        """

        return {
            **super().to_dict(),
        }
