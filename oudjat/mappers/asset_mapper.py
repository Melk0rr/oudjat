"""
A generic module that helps connectors to map data into assets.
"""

from collections.abc import Callable, Sequence
from typing import Any, override

from oudjat.core.asset import AssetBoundType
from oudjat.core.mapper import Mapper, MappingRegistry

type AssetMappingCallback = Callable[["AssetBoundType", dict[str, Any], "MappingRegistry"], None]

class AssetMapper(Mapper):
    """
    A generic mapper that turns data (dict or list of dicts) into Asset instances.
    """

    # ****************************************************************
    # Class methods - engine

    @override
    @classmethod
    def _build_kwargs(
        cls,
        record: dict[str, Any],
        map_cls: type["AssetBoundType"],
        mapping_registry: "MappingRegistry",
    ) -> dict[str, Any]:
        """
        Return parameters required to instanciate the provided Asset class.

        Args:
            record (dict[str, Any])           : The base data record from which the Asset class will be instanciated.
            map_cls (type[AssetBoundType])    : The Asset class that will be instanciated
            mapping_registry (MappingRegistry): The mapping registry used to set the constructor parameter: value tuples

        Returns:
            dict[str, Any]: A dictionary of the resulting constructor arguments
        """

        return super()._build_kwargs(record, map_cls, mapping_registry)

    @override
    @classmethod
    def map_one(
        cls,
        record: dict[str, Any],
        map_cls: type["AssetBoundType"],
        mapping_registry: "MappingRegistry | list[MappingRegistry]",
        callback: "AssetMappingCallback | None" = None,
    ) -> "AssetBoundType":
        """
        Map a single data record into an instance of the provided asset class.

        Args:
            record (dict[str, Any])               : The data record to map
            map_cls (type[AssetBoundType])        : The class the record will be mapped into
            mapping_registry (list[MappingValue]) : The mapping registry used to map the record
            callback (AssetMappingCallback | None): A callback function to run after the asset has been mapped

        Returns:
            AssetBoundType: The mapped asset
        """

        return super().map_one(record, map_cls, mapping_registry, callback)

    @override
    @classmethod
    def map_many(
        cls,
        records: Sequence[dict[str, Any]],
        map_cls: type["AssetBoundType"],
        mapping_registry: "MappingRegistry | list[MappingRegistry]",
        key_cb: Callable[[dict[str, Any]], str],
        record_cb: Callable[..., dict[str, Any]] | None = None,
        asset_cb: "AssetMappingCallback | None" = None,
    ) -> dict[str, "AssetBoundType"]:
        """
        Map multiple data record into instances of the provided asset class.

        Args:
            records (dict[str, Any])                              : The data record to map
            map_cls (type[AssetBoundType])                        : The class the record will be mapped into
            mapping_registry (list[MappingValue])                 : The mapping registry used to map the record
            record_cb (Callable[[dict[str, Any]], dict[str, Any]]): A callback function to run after the asset has been mapped
            asset_cb (AssetMappingCallback)                       : A callback function to run after the asset has been mapped
            key_cb (Callable[dict[str, Any], str] | None)         : A callback function to provide a key to associate wih the mapped asset

        Returns:
            dict[str, AssetBoundType]: A dictionary of mapped Assets
        """

        return super().map_many(records, map_cls, mapping_registry, key_cb, record_cb, asset_cb)

    # ****************************************************************
    # Static methods

