"""
A generic module that helps connectors to map data into assets.
"""

from collections.abc import Sequence
from typing import Any, Callable, TypeAlias, override

from oudjat.core.asset import AssetBoundType
from oudjat.core.mapper import Mapper, MappingRegistry
from oudjat.core.software.exceptions import AmbiguousReleaseException
from oudjat.core.software.os import OperatingSystem, OSFamily, OSOption, OSRelease
from oudjat.core.software.os.exceptions import NotImplementedOSOption
from oudjat.core.software.os.operating_system import OSReleaseListFilter
from oudjat.core.software.software_edition import SoftwareEdition
from oudjat.core.software.software_release_version import SoftwareReleaseVersion
from oudjat.utils import Context

MappingOSTuple: TypeAlias = tuple[
    "OperatingSystem | None", "OSRelease | None", "SoftwareEdition | None"
]

AssetMappingCallback: TypeAlias = Callable[["AssetBoundType", dict[str, Any], "MappingRegistry"], None]

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
        mapping_registry: "MappingRegistry" | list["MappingRegistry"],
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
        mapping_registry: "MappingRegistry" | list["MappingRegistry"],
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
