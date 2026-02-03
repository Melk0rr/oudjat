"""
A generic module to handle data mapping.
"""

import inspect
import logging
from collections.abc import Sequence
from ctypes import ArgumentError
from decimal import Context
from typing import Any, Callable, TypeAlias

MappingValue: TypeAlias = Any | Callable[[dict[str, Any]], Any]
MappingRegistry: TypeAlias = dict[str, "MappingValue"]
MappingRegistryFunc: TypeAlias = Callable[..., "MappingRegistry"]
MappingCallback: TypeAlias = Callable[[Any, dict[str, Any], "MappingRegistry"], None]

class Mapper:
    """
    A generic class to map any data record into any class.
    """

    # ****************************************************************
    # Attributes & Constructors

    logger: "logging.Logger" = logging.getLogger(__name__)

    @classmethod
    def _merge_registries(cls, registries: list["MappingRegistry"]) -> "MappingRegistry":
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

    @classmethod
    def map_value(cls, map_val: "MappingValue", *args: Any) -> Any:
        """
        Map a single kwarg value into its final value.

        Args:
            record (dict[str, Any]): Base record to pass to the value mapping function
            map_val (MappingValue) : Final value or function to obtain it
            *args (Any)            : Optional arguments to pass to the value function

        Returns:
            type and description of the returned object.
        """

        while callable(map_val):
            map_val = map_val(*args)

        return map_val


    @classmethod
    def _build_kwargs(
        cls,
        record: dict[str, Any],
        map_cls: type[Any],
        mapping_registry: "MappingRegistry",
    ) -> dict[str, Any]:
        """
        Return parameters required to instanciate the provided Asset class.

        Args:
            record (dict[str, Any])           : The base data record from which the Asset class will be instanciated.
            map_cls (type[Any])               : The class that will be instanciated
            mapping_registry (MappingRegistry): The mapping registry used to set the constructor parameter: value tuples
            *args (Any)                       : Additional arguments to pass to the mapping function

        Returns:
            dict[str, Any]: A dictionary of the resulting constructor arguments
        """

        context = Context()

        constructor_sig = inspect.signature(map_cls.__init__)
        params = {name: p for name, p in constructor_sig.parameters.items() if name != "self"}
        required_params = {name for name, p in params.items() if p.default is p.empty}

        kwargs: dict[str, Any] = {}
        for target_key, map_val in mapping_registry.items():

            # If target key is not a valid argument accepted by the constructor
            # and the constructor does not accept kwargs: continue
            if target_key not in params and "kwargs" not in params:
                cls.logger.warning(f"{context}::{target_key} is not accepted by {map_cls.__name__} constructor")
                continue

            kwargs[target_key] = cls.map_value(map_val, record)

            if target_key in required_params:
                required_params.remove(target_key)

        if len(required_params) > 0:
            raise ArgumentError(
                f"{context}::{map_cls.__name__} constructor requires {list(required_params)} argument"
            )

        return kwargs

    @classmethod
    def map_one(
        cls,
        record: dict[str, Any],
        map_cls: type[Any],
        mapping_registry: "MappingRegistry" | list["MappingRegistry"],
        callback: "MappingCallback | None" = None,
    ) -> Any:
        """
        Map a single data record into an instance of the provided asset class.

        Args:
            record (dict[str, Any])              : The data record to map
            map_cls (type[Any])                  : The class the record will be mapped into
            mapping_registry (list[MappingValue]): The mapping registry used to map the record
            callback (Callable[..., Any])        : A callback function to run after the asset has been mapped

        Returns:
            Any: The mapped class instance
        """

        cls.logger.debug(f"{Context()}::Mapping {record} > {map_cls.__name__} : {mapping_registry}")
        if isinstance(mapping_registry, list):
            mapping_registry = cls._merge_registries(mapping_registry)

        kwargs = cls._build_kwargs(record, map_cls, mapping_registry)
        asset = map_cls(**kwargs)

        if callback is not None:
            callback(asset, record, mapping_registry)

        return asset

    @classmethod
    def map_many(
        cls,
        records: Sequence[dict[str, Any]],
        map_cls: type[Any],
        mapping_registry: "MappingRegistry" | list["MappingRegistry"],
        key_cb: Callable[[dict[str, Any]], str],
        record_cb: Callable[..., dict[str, Any]] | None = None,
        asset_cb: "MappingCallback | None" = None,
    ) -> dict[str, Any]:
        """
        Map multiple data record into instances of the provided asset class.

        Args:
            records (dict[str, Any])                              : The data record to map
            map_cls (type[Any])                                   : The class the record will be mapped into
            mapping_registry (list[MappingValue])                 : The mapping registry used to map the record
            key_cb (Callable[dict[str, Any], str] | None)         : A callback function to provide a key to associate wih the mapped asset
            record_cb (Callable[[dict[str, Any]], dict[str, Any]]): A callback function to run after the asset has been mapped
            asset_cb (MappingCallback)                            : A callback function to run after the asset has been mapped

        Returns:
            dict[str, Any]: A dictionary of mapped instances based on the provided class
        """

        res = {}
        for record in records:
            cls.logger.debug(f"{Context()}::Mapping record > {record}")

            a = cls.map_one(
                record=(record_cb(record) if record_cb else record),
                map_cls=map_cls,
                mapping_registry=mapping_registry,
                callback=asset_cb,
            )

            res[key_cb(record)] = a

        return res

