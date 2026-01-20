"""
A generic module that helps connectors to map data into assets.
"""

import inspect
from ctypes import ArgumentError
from dataclasses import dataclass
from typing import Any, Callable, TypeAlias

from oudjat.core.asset import AssetBoundType
from oudjat.utils import Context

from .connector import Connector, ConnectorBoundType


@dataclass
class MappingValue:
    """
    AssetMapper mapping value tuple.

    Attributes:
        target_key (str)                : The new key to use that should match an Asset constructor argument.
        transformer (Callable[Any], Any): The transformer function to transform the record value
    """

    target_key: str
    transformer: Callable[[Any], Any] | None = None


MappingRegistry: TypeAlias = dict[str, "MappingValue"]


class AssetMapper:
    """
    A generic mapper that turns data (dict or list of dicts) into Asset instances.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self) -> None:
        """
        Create a new AssetMapper instance.
        """

        self._connector: "ConnectorBoundType | None" = None

    # ****************************************************************
    # Methods

    def _merge_registries(self, registries: list["MappingRegistry"]) -> "MappingRegistry":
        """
        Merge several registries into a single one.

        Args:
            registries (list[MappingRegistry]): Registries to merge

        Returns:
            dict[str, MappingValue]: Merged mapping registry
        """

        registry: "MappingRegistry" = {}
        for md in registries:
            registry.update(md)

        return registry

    def _transform(self, value: Any, transform: Callable[[Any], Any]) -> Any:
        """
        Transform the provided value based on the transform function.

        Args:
            value (Any)                     : The value to transform
            transform (Callable[[Any], Any]): The transform function used to transform the profided value

        Returns:
            Any: The transformed value
        """

        try:
            return transform(value)

        except Exception as e:
            raise ValueError(
                f"{Context()}::Could not transform {value} based on profided transform function"
            ) from e

    def _build_kwargs(
        self,
        record: dict[str, Any],
        asset_cls: type["AssetBoundType"],
        mapping_registry: "MappingRegistry",
    ) -> dict[str, Any]:
        """
        Return parameters required to instanciate the provided Asset class.

        Args:
            record (dict[str, Any])         : The base data record from which the Asset class will be instanciated.
            asset_cls (type[AssetBoundType]): The Asset class that will be instanciated
            mapping_registry (MappingRegistry): The mapping registry used to set the constructor parameter: value tuples

        Returns:
            dict[str, Any]: A dictionary of the resulting constructor arguments
        """

        constructor_sig = inspect.signature(asset_cls.__init__)
        params = {name: p for name, p in constructor_sig.parameters.items() if name != "self"}

        kwargs: dict[str, Any] = {}
        for src_key, src_value in record.items():
            if src_key not in mapping_registry:
                continue

            target_key, transform = (
                mapping_registry[src_key].target_key,
                mapping_registry[src_key].transformer,
            )

            # If target key is not a valid argument accepted by the constructor
            # and the constructor does not accept kwargs: continue
            if target_key not in params and "kwargs" not in params:
                continue

            kwargs[target_key] = (
                self._transform(src_value, transform) if transform is not None else src_value
            )

        required_params = { name for name, p in params.items() if p.default is p.empty }
        for p in required_params:
            if p not in kwargs:
                raise ArgumentError(f"{Context()}::{asset_cls.__name__} constructor requires {p} argument")

        return kwargs

    def map_one(
        self,
        record: dict[str, Any],
        asset_cls: type["AssetBoundType"],
        mapping_registry: MappingRegistry | list["MappingRegistry"],
        callback: Callable[..., None],
    ) -> "AssetBoundType":
        """
        Map a single data record into an instane of the provided asset class.

        Args:
            record (dict[str, Any])               : The data record to map
            asset_cls (type[AssetBoundType])      : The class the record will be mapped into
            mapping_registry (list[MappingValue]) : The mapping registry used to map the record
            callback (Callable[..., Any])         : A list of callback functions to run after the asset has been mapped

        Returns:
            AssetBoundType: The mapped asset
        """

        if not isinstance(mapping_registry, list):
            mapping_registry = [mapping_registry]

        merged_registry = self._merge_registries(mapping_registry)
        kwargs = self._build_kwargs(record, asset_cls, merged_registry)

        asset = asset_cls(**kwargs)

        if callback is not None:
            callback(asset, record)

        return asset


