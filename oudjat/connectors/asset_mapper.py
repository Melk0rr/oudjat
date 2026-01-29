"""
A generic module that helps connectors to map data into assets.
"""

import inspect
import logging
from collections.abc import Sequence
from ctypes import ArgumentError
from typing import Any, Callable, TypeAlias

from oudjat.core.asset import AssetBoundType
from oudjat.core.software.exceptions import AmbiguousReleaseException
from oudjat.core.software.os import OperatingSystem, OSFamily, OSOption, OSRelease
from oudjat.core.software.os.exceptions import NotImplementedOSOption
from oudjat.core.software.os.operating_system import OSReleaseListFilter
from oudjat.core.software.software_edition import SoftwareEdition
from oudjat.core.software.software_release_version import SoftwareReleaseVersion
from oudjat.utils import Context

from .connector import ConnectorBoundType

MappingValue: TypeAlias = tuple[str, Callable[[Any], Any] | None]
MappingRegistry: TypeAlias = dict[str, "MappingValue"]
MappingCallback: TypeAlias = Callable[["AssetBoundType", dict[str, Any]], None]

MappingOSTuple: TypeAlias = tuple[
    "OperatingSystem | None", "OSRelease | None", "SoftwareEdition | None"
]


class AssetMapper:
    """
    A generic mapper that turns data (dict or list of dicts) into Asset instances.
    """

    # ****************************************************************
    # Attributes & Constructors

    logger: "logging.Logger" = logging.getLogger(__name__)

    def __init__(self) -> None:
        """
        Create a new AssetMapper instance.
        """

        self._connector: "ConnectorBoundType | None" = None

    # ****************************************************************
    # Methods - engine

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

            target_key, transform = mapping_registry[src_key]

            # If target key is not a valid argument accepted by the constructor
            # and the constructor does not accept kwargs: continue
            if target_key not in params and "kwargs" not in params:
                continue

            kwargs[target_key] = (
                self._transform(src_value, transform) if transform else src_value
            )

        required_params = {name for name, p in params.items() if p.default is p.empty}
        for p in required_params:
            if p != "kwargs" and p not in kwargs:
                raise ArgumentError(
                    f"{Context()}::{asset_cls.__name__} constructor requires {p} argument"
                )

        return kwargs

    def map_one(
        self,
        record: dict[str, Any],
        asset_cls: type["AssetBoundType"],
        mapping_registry: "MappingRegistry" | list["MappingRegistry"],
        callback: "MappingCallback | None" = None,
    ) -> "AssetBoundType":
        """
        Map a single data record into an instance of the provided asset class.

        Args:
            record (dict[str, Any])               : The data record to map
            asset_cls (type[AssetBoundType])      : The class the record will be mapped into
            mapping_registry (list[MappingValue]) : The mapping registry used to map the record
            callback (Callable[..., Any])         : A callback function to run after the asset has been mapped

        Returns:
            AssetBoundType: The mapped asset
        """

        self.__class__.logger.debug(f"{Context()}::Maping {record} > {asset_cls.__name__} : {mapping_registry}")
        if isinstance(mapping_registry, list):
            mapping_registry = self._merge_registries(mapping_registry)

        kwargs = self._build_kwargs(record, asset_cls, mapping_registry)
        asset = asset_cls(**kwargs)

        if callback is not None:
            callback(asset, record)

        return asset

    def map_many(
        self,
        records: Sequence[dict[str, Any]],
        asset_cls: type["AssetBoundType"],
        mapping_registry: "MappingRegistry" | list["MappingRegistry"],
        record_cb: Callable[..., dict[str, Any]] | None = None,
        asset_cb: "MappingCallback | None" = None,
        key_cb: Callable[[dict[str, Any]], str] | None = None,
    ) -> dict[str, "AssetBoundType"]:
        """
        Map multiple data record into instances of the provided asset class.

        Args:
            records (dict[str, Any])                              : The data record to map
            asset_cls (type[AssetBoundType])                      : The class the record will be mapped into
            mapping_registry (list[MappingValue])                 : The mapping registry used to map the record
            record_cb (Callable[[dict[str, Any]], dict[str, Any]]): A callback function to run after the asset has been mapped
            asset_cb (MappingCallback)                            : A callback function to run after the asset has been mapped
            key_cb (Callable[dict[str, Any], str] | None)         : A callback function to provide a key to associate wih the mapped asset

        Returns:
            dict[str, AssetBoundType]: A dictionary of mapped Assets
        """

        res = {}
        for record in records:
            self.__class__.logger.debug(f"{Context()}::Mapping record > {record}")

            a = self.map_one(
                record=(record_cb(record) if record_cb else record),
                asset_cls=asset_cls,
                mapping_registry=mapping_registry,
                callback=asset_cb,
            )

            res[key_cb(record) if key_cb else a.id] = a

        return res

    # ****************************************************************
    # Static methods

    @staticmethod
    def guess_os_edition(
        os: "str | OperatingSystem", os_edition_str: str | None = None
    ) -> "SoftwareEdition | None":
        """
        Return a SoftwareEdition instance based on the computer operatingSystem attribute.

        Args:
            os (OperatingSystem)       : The OS from which the edition should be retrieved
            os_edition_str (str | None): The OS string that may contain the edition

        Returns:
            SoftwareEdition | None: The SoftwareEdition instance that matches the computer operatingSystem attribute if any
        """

        if os_edition_str is None:
            return None

        if not isinstance(os, OperatingSystem):
            os_guess = AssetMapper.guess_os(os)
            if os_guess is None:
                return None

            os = os_guess

        os_edition_match: list["SoftwareEdition"] = os.matching_editions(os_edition_str)
        if len(os_edition_match) == 0 and "Standard" in os.editions.keys():
            os_edition_match.append(os.editions["Standard"])

        return os_edition_match[0] if len(os_edition_match) != 0 else None

    @staticmethod
    def guess_os(os_str: str) -> "OperatingSystem | None":
        """
        Try to guess the OperatingSystem from a string.

        Args:
            os_str (str): The string that may contain an operating system reference

        Returns:
            OperatingSystem | None: The OperatingSystem guessed from the provided string
        """

        context = Context()

        os_family_opt_match = OSFamily.search_os_family_opt(os_str)
        if os_family_opt_match is None:
            AssetMapper.logger.error(f"{context}::Could not guess OperatingSystem from {os_str}")
            return None

        os_family_opt, os_family_str = os_family_opt_match

        if os_family_opt.name not in OSOption._member_names_:
            raise NotImplementedOSOption(
                f"{context}::{os_family_opt.name}({os_family_str}) is not a valid OSOption"
            )

        return OSOption[os_family_opt.name]()

    @staticmethod
    def guess_os_release(
        os: "str | OperatingSystem", os_ver: str, filters: list["OSReleaseListFilter"]
    ) -> "OSRelease | None":
        """
        Return an OS release instance based on the computer operatingSystemVersion attribute.

        Args:
            os (str)                           : Either a string from which guess OS infos or an OperatingSystem instance
            os_ver (str)                       : A string that contain specifically the release version
            filters (list[OSReleaseListFilter]): A list of filters to retrieve a unique release

        Returns:
            OSRelease | None: The OS release that matches the provided strings
        """

        context = Context()
        if not isinstance(os, OperatingSystem):
            os_guess = AssetMapper.guess_os(os)
            if os_guess is None:
                return None

            os = os_guess

        candidates = os.release(os_ver)
        if not isinstance(candidates, list):
            return candidates

        if candidates.is_empty():
            return None

        res = candidates.unique(*filters)
        if res is None:
            raise AmbiguousReleaseException(
                f"{context}::Unable to resolve a unique release for {os_ver}"
            )

        return res

    @staticmethod
    def map_os(
        os_str: str | None = None,
        os_ver: str | None = None,
        filters: list["OSReleaseListFilter"] | None = None,
    ) -> "MappingOSTuple":
        """
        Return a tuple with 3 OS elements guessed from an OS string, and a release version.

        The final tuple contains those 3 elements
        1 - An OperatingSystem instance, or None if it can't be guessed from the provided argument
        2 - An OSRelease instance, or None if it can't be guessed from the provided argument
        3 - A SoftwareEdition instance, or None if it can't be guessed from the provided argument

        Args:
            os_str (str | None)                : A string that may contain operating system, edition and optionaly release details
            os_ver (str | None)                : A software release version string
            filters (list[OSReleaseListFilter]): A list of filter function to apply on a SoftwareReleaseList to narrow it down to a unique release

        Returns:
            tuple["OperatingSystem | None", "OSRelease | None", "SoftwareEdition | None"]: A tuple containing the 3 mentioned elements

        Example:
            map_os("Windows 11 Enterprise", "10.0.26200", [])
        """

        if filters is None:
            filters = []

        res = (None, None, None)
        if os_str is not None:
            if os_ver is None:
                os_ver = SoftwareReleaseVersion.search_release_version(os_str)

            os = AssetMapper.guess_os(os_str)

            if os is not None:
                os_rel = AssetMapper.guess_os_release(os, os_ver or os_str, filters=filters)
                os_edition = AssetMapper.guess_os_edition(os, os_str)

                res = os, os_rel, os_edition

        return res
