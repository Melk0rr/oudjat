"""A simple module that lists operating system options."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from oudjat.connectors.endoflife.definitions import EOL_CACHE_PATH
from oudjat.core.computer.computer_type import ComputerType
from oudjat.utils import Context, FileUtils

from ..exceptions import AmbiguousReleaseException
from ..software_edition import DEFAULT_SOFTWARE_EDITION, SoftwareEdition
from ..software_release import SoftwareReleaseList
from ..software_release_version import SoftwareReleaseVersion
from .exceptions import NotImplementedOSOption
from .operating_system import OperatingSystem, OSRelease, OSReleaseListFilter
from .os_families import OSFamily
from .windows import WindowsEdition

type MappingOSTuple = tuple[
    "OperatingSystem | None", "OSRelease | None", "SoftwareEdition | None"
]

@dataclass
class OSOptionProps:
    """
    A helper class to define OSOption elements property types.

    Attributes:
        cls (OSRelease)               : The class associated with the option
        releases (OSReleaseImportDict): The releases associated with the option
    """

    cls: type["OperatingSystem"]
    attributes: dict[str, Any]
    instance: "OperatingSystem | None" = None


class OSOption(Enum):
    """An enumeration of OSes."""

    RHEL = OSOptionProps(
        cls=OperatingSystem,
        attributes={
            "os_id": "rhel",
            "name": "Red Hat Enterprise Linux",
            "label": "red-hat-enterprise-linux",
            "editor": "Red Hat",
            "os_family": OSFamily.LINUX,
            "computer_type": ComputerType.SERVER,
            "description": "Red Hat Enterprise Linux is a Linux distribution developed by Red Hat for the commercial market",
            "editions": DEFAULT_SOFTWARE_EDITION,
            "tags": ["linux-distribution", "red-hat"],
        },
    )

    WINDOWS = OSOptionProps(
        cls=OperatingSystem,
        attributes={
            "os_id": "windows",
            "name": "Windows",
            "label": "windows",
            "editor": "Microsoft Corporation",
            "os_family": OSFamily.WINDOWS,
            "computer_type": ComputerType.WORKSTATION,
            "description": "Microsoft Windows is the operating system developed by Microsoft to run on workstations",
            "editions": WindowsEdition.WINDOWS.value,
            "tags": ["microsoft", "windows"],
        },
    )

    WINDOWSSERVER = OSOptionProps(
        cls=OperatingSystem,
        attributes={
            "os_id": "windowsserver",
            "name": "Windows Server",
            "label": "windows-server",
            "editor": "Microsoft Corporation",
            "os_family": OSFamily.WINDOWS,
            "computer_type": ComputerType.SERVER,
            "description": "Microsoft Windows is the operating system developed by Microsoft to run on servers",
            "editions": WindowsEdition.WINDOWSSERVER.value,
            "tags": ["microsoft", "windows"],
        },
    )

    @property
    def instance(self) -> "OperatingSystem | None":
        """
        Return the instance of this option.

        Returns:
            OperatingSystem | None: OSOption instance
        """

        return self._value_.instance

    @property
    def attributes(self) -> dict[str, Any]:
        """
        Return the attributes associated with the option.

        Returns:
            dict[str, Any]: The dictionary of attributes to pass to the option class
        """

        return self._value_.attributes

    def _opt_cache_path(self, id: int | str) -> Path:
        """
        Return the cache path based on a provided OSOption id

        Args:
            id (int | str): The id of the OS option.

        Returns:
            Path: The cache path for the OS option matching the provided id
        """

        return Path(EOL_CACHE_PATH) / f"{id}.json"

    def __call__(self) -> "OperatingSystem":
        """
        Return the operating system of the option by calling it.

        Returns:
            OperatingSystem: The operating system that corresponds to the option
        """

        if self._value_.instance is None:
            self._value_.instance = self._value_.cls(**self.attributes)

            release_data_path = self._opt_cache_path(self._value_.instance.id)

            if not release_data_path.exists():
                raise FileNotFoundError(f"{Context()}::Cache could not be retrieved. Make sure you generated it using endoflife asset mapper.")

            release_data = FileUtils.import_json(release_data_path)[0]

            self._value_.instance.releases = OSRelease.gen_releases(release_data)

        return self._value_.instance

    @staticmethod
    def per_family(family: "OSFamily") -> dict[str, "OSOption"]:
        """
        Return a dictionary of OSOption that are bound to the provided OSFamily.

        Args:
            family (OSFamily): The OSFamily the options must be bound to

        Returns:
            dict[str, OSOption]: A dictionary of OSOption bound to the provided family
        """

        return {
            option.name: option for option in OSOption if option.name in family.names
        }

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
            os_guess = OSOption.guess_os(os)
            if os_guess is None:
                return None

            os = os_guess

        os_edition_match: list[SoftwareEdition] = os.matching_editions(os_edition_str)
        if len(os_edition_match) == 0 and "Standard" in os.editions:
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
            # .logger.error(f"{context}::Could not guess OperatingSystem from {os_str}")
            return None

        os_family_opt, os_family_str = os_family_opt_match

        if os_family_opt.name not in OSOption._member_names_:
            raise NotImplementedOSOption(
                f"{context}::{os_family_opt.name}({os_family_str}) is not a valid OSOption"
            )

        return OSOption[os_family_opt.name]()

    @staticmethod
    def guess_os_release(
        os: "str | OperatingSystem", os_ver: str, filters: list[OSReleaseListFilter]
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
            os_guess = OSOption.guess_os(os)
            if os_guess is None:
                return None

            os = os_guess

        candidates = os.release(os_ver)
        if not isinstance(candidates, SoftwareReleaseList):
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
    ) -> MappingOSTuple:
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

            os = OSOption.guess_os(os_str)

            if os is not None:
                os_rel = OSOption.guess_os_release(os, os_ver or os_str, filters=filters)
                os_edition = OSOption.guess_os_edition(os, os_str)

                res = os, os_rel, os_edition

        return res
