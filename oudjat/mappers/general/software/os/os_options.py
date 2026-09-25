"""A simple module that lists operating system options."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TypedDict

from oudjat.core.software import SoftwareEditionDict, SoftwareReleaseVersion
from oudjat.core.software.os.operating_system import (
    OperatingSystem,
    OSRelease,
    OSReleaseListFilter,
)
from oudjat.core.software.os.windows import WindowsEdition
from oudjat.core.software.software_edition import (
    DEFAULT_SOFTWARE_EDITION,
    SoftwareEdition,
)
from oudjat.core.software.software_release import SoftwareReleaseList
from oudjat.mappers.connectors.endoflife.asset_mapper import EOLAssetMapper
from oudjat.utils import Context, FileUtils

from .os_families import OSFamily

CACHE_PATH = FileUtils.project_root() / ".cache"
SOFTWARE_CACHE_PATH = CACHE_PATH / "software"


class NotImplementedOSOption(KeyError):
    """
    A helper class to handle not implemented os option.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of NotImplementedOSOption.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)


class AmbiguousReleaseException(Exception):
    """
    A helper class to handle ambiguous SoftwareRelease resolution.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of AmbiguousReleaseException.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)


type MappingOSTuple = tuple[
    "OperatingSystem | None", "OSRelease | None", "SoftwareEdition | None"
]


class OSOptAttributes(TypedDict):
    """
    A simple class to specify OSOption attributes properties.

    Attributes:
        os_id         (str)                : A short string to identify the os. Preferably matching endoflife.date product
        name          (str)                : The name of the OS
        label         (str)                : A string (without spaces) comparable to an id but more explicit
        editor        (str)                : The name of the editor that maintains the OS
        os_family     (str | OSFamily)     : The family of operating system the OS belongs to
        description   (str)                : A string that describes the OS
        editions      (SoftwareEditionDict): A dictionary of editions available for that os. Default will resolve to a default standard edition
        tags          (list[str])          : A list of tags that describe the OS

    """

    os_id: str
    name: str
    label: str
    editor: str
    os_family: str | OSFamily
    description: str
    editions: SoftwareEditionDict
    tags: list[str]


@dataclass
class OSOptionProps:
    """
    A helper class to define OSOption elements property types.

    Attributes:
        cls (OSRelease)               : The class associated with the option
        releases (OSReleaseImportDict): The releases associated with the option
    """

    cls: type["OperatingSystem"]
    attributes: OSOptAttributes
    instance: "OperatingSystem | None" = None


# TODO: Use a JSON based logic + generate Enum elements from it if possible or change Enum to regular class
class OSOption(Enum):
    """An enumeration of OSes."""

    ALMALINUX = OSOptionProps(
        cls=OperatingSystem,
        attributes={
            "os_id": "almalinux",
            "name": "Alma Linux",
            "label": "alma-linux",
            "editor": "Andrew Lukoshko",
            "os_family": OSFamily.LINUX,
            "description": "Alma Linux is an open source, community-owned and governed, forever-free enterprise Linux distribution. It is focused on long-term stability, providing a robust production-grade platform. AlmaLinux OS is binary-compatible with RHEL. It is owned and controlled by the non-profit AlmaLinux OS Foundation, and managed by a community-elected board of directors and the self-managed AlmaLinux Engineering Steering Committee",
            "editions": DEFAULT_SOFTWARE_EDITION,
            "tags": ["linux-distribution"],
        },
    )

    CENTOS = OSOptionProps(
        cls=OperatingSystem,
        attributes={
            "os_id": "centos",
            "name": "CentOS",
            "label": "community-enterprise-operating-system",
            "editor": "Lance Davis",
            "os_family": OSFamily.LINUX,
            "description": "CentOS was a Linux distribution that provided a free, enterprise-class, community-supported computing platform functionally compatible with RHEL",
            "editions": DEFAULT_SOFTWARE_EDITION,
            "tags": ["linux-distribution", "red-hat"],
        },
    )

    DEBIAN = OSOptionProps(
        cls=OperatingSystem,
        attributes={
            "os_id": "debian",
            "name": "Debian",
            "label": "debian",
            "editor": "",
            "os_family": OSFamily.LINUX,
            "description": "Debian is a free operating system for your computer. The Debian stable branch is the most popular edition for personal computers and network servers, and is used as the basis for many other Linux distributions",
            "editions": DEFAULT_SOFTWARE_EDITION,
            "tags": ["linux-distribution"],
        },
    )

    FREEBSD = OSOptionProps(
        cls=OperatingSystem,
        attributes={
            "os_id": "freebsd",
            "name": "FreeBSD",
            "label": "freebsd",
            "editor": "FreeBSD Project",
            "os_family": OSFamily.UNIX,
            "description": "FreeBSD is an operating system used to power modern servers, desktops, and embedded platforms",
            "editions": DEFAULT_SOFTWARE_EDITION,
            "tags": ["unix-distribution", "bsd-distribution"],
        },
    )

    ORACLELINUX = OSOptionProps(
        cls=OperatingSystem,
        attributes={
            "os_id": "oraclelinux",
            "name": "Oracle Linux",
            "label": "oracle-linux",
            "editor": "Oracle",
            "os_family": OSFamily.LINUX,
            "description": "Oracle Linux is an Open Source, free RHEL derivative developed by Oracle to be a 100% application binary compatible alternative to Red Hat Enterprise Linux",
            "editions": DEFAULT_SOFTWARE_EDITION,
            "tags": ["linux-distribution", "oracle"],
        },
    )

    ORACLESOLARIS = OSOptionProps(
        cls=OperatingSystem,
        attributes={
            "os_id": "solaris",
            "name": "Oracle Solaris",
            "label": "oracle-solaris",
            "editor": "Oracle",
            "os_family": OSFamily.UNIX,
            "description": "Oracle Solaris is a proprietary Unix operating system originally developed by Sun Microsystems. After the Sun acquisition by Oracle in 2010, it was renamed Oracle Solaris. It supports SPARC and x86-64 workstations and servers. It is known for its stability, performance, scalability and innovative features such as DTrace or ZFS",
            "editions": DEFAULT_SOFTWARE_EDITION,
            "tags": ["unix-distribution", "oracle"],
        },
    )

    RHEL = OSOptionProps(
        cls=OperatingSystem,
        attributes={
            "os_id": "rhel",
            "name": "Red Hat Enterprise Linux",
            "label": "red-hat-enterprise-linux",
            "editor": "Red Hat",
            "os_family": OSFamily.LINUX,
            "description": "Red Hat Enterprise Linux is a Linux distribution developed by Red Hat for the commercial market",
            "editions": DEFAULT_SOFTWARE_EDITION,
            "tags": ["linux-distribution", "red-hat"],
        },
    )

    ROCKYLINUX = OSOptionProps(
        cls=OperatingSystem,
        attributes={
            "os_id": "rockylinux",
            "name": "Rocky Linux",
            "label": "rocky-linux",
            "editor": "The Rocky Enterprise Software Foundation",
            "os_family": OSFamily.LINUX,
            "description": " Rocky Linux is a Linux distribution intended to be a downstream, complete binary-compatible release using the Red Hat Enterprise Linux (RHEL) operating system source code. The project is led by Gregory Kurtzer, founder of the CentOS project",
            "editions": DEFAULT_SOFTWARE_EDITION,
            "tags": ["linux-distribution"],
        },
    )

    SLES = OSOptionProps(
        cls=OperatingSystem,
        attributes={
            "os_id": "sles",
            "name": "SUSE Linux Enterprise Server",
            "label": "suse-linux-enterprise-server",
            "editor": "SUSE",
            "os_family": OSFamily.LINUX,
            "description": "SUSE Linux Enterprise Server is a modular linux distribution for both multimodal and traditional IT",
            "editions": DEFAULT_SOFTWARE_EDITION,
            "tags": ["linux-distribution", "suse"],
        },
    )

    UBUNTU = OSOptionProps(
        cls=OperatingSystem,
        attributes={
            "os_id": "ubuntu",
            "name": "Ubuntu",
            "label": "ubuntu",
            "editor": "Canonical",
            "os_family": OSFamily.LINUX,
            "description": "Ubuntu is a free and open-source Linux distribution based on Debian. Ubuntu is officially released in three editions: Desktop, Server, and Core",
            "editions": DEFAULT_SOFTWARE_EDITION,
            "tags": ["linux-distribution", "canonical"],
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
    def attributes(self) -> OSOptAttributes:
        """
        Return the attributes associated with the option.

        Returns:
            dict[str, Any]: The dictionary of attributes to pass to the option class
        """

        return self._value_.attributes

    def _opt_cache_path(self) -> Path:
        """
        Return the cache path of the current OS option based on its id

        Returns:
            Path: The cache path for the OS option matching the provided id
        """

        return Path(SOFTWARE_CACHE_PATH) / f"{self.attributes['os_id']}.json"

    def gen_opt_cache(self) -> bool:
        """
        Generate cache for an OS option.

        Returns:
            bool: True if the cache could be generated. False otherwise
        """

        path = self._opt_cache_path()
        mapper = EOLAssetMapper()

        # Delete the cache if it exists
        if path.exists():
            path.unlink()

        if self.attributes["os_id"] == "windows":
            data = mapper.windows()

        elif self.attributes["os_id"] == "windowsserver":
            data = mapper.windows_server()

        else:
            data = mapper.unix(self.attributes["os_id"])

        FileUtils.export_json(data.to_dict(), path)

        return path.exists()

    def __call__(self) -> "OperatingSystem":
        """
        Return the operating system of the option by calling it.

        Returns:
            OperatingSystem: The operating system that corresponds to the option
        """

        if self._value_.instance is None:
            self._value_.instance = self._value_.cls(**self.attributes)

            release_data_path = self._opt_cache_path()

            # Ensures cache dir exists
            SOFTWARE_CACHE_PATH.mkdir(parents=True, exist_ok=True)

            if not release_data_path.exists():
                self.gen_opt_cache()

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
    def _guess_os_candidates_by_version(
        os: "OperatingSystem", os_ver: str
    ) -> SoftwareReleaseList[OSRelease] | None:
        """
        Try to guess OS release candidates based on a provided version.

        1. Simply try to retrieve a SoftwareReleaseList based on the exact provided version.
        2. If no candidates could be retrieved, try to find some by comparing version ranges.
        3. If no candidates could be retrieved, try to search the closest matching version.

        Args:
            os     (OperatingSystem): The OperatingSystem instance which stores the releases to lookup.
            os_ver (str)            : The version to look for.

        Returns:
            SoftwareReleaseList: A list of release candidates, if any could be retrieved.
        """

        version = SoftwareReleaseVersion(os_ver)

        # 1: Try to retrieve the exact provided version
        candidates = os.releases.get(str(version))

        # 2: Try to find a matching version by comparing the provided one with each release initial and last versions
        if candidates is None:
            candidates = os.releases.find_version_in_range(version)

        # 3: Try to find the closest matching version and retrieve it
        if candidates is None:
            closest_version = os.releases.find_closest_version(version)

            if closest_version is not None:
                candidates = os.releases.get(str(closest_version))

        return candidates

    @staticmethod
    def guess_os_release(
        os: "str | OperatingSystem",
        os_str: str | None = None,
        os_ver: str | None = None,
        filters: list[OSReleaseListFilter] | None = None,
    ) -> "OSRelease | None":
        """
        Return an OS release instance based on the computer operatingSystemVersion attribute.

        Args:
            os      (str)                      : Either a string from which guess OS infos or an OperatingSystem instance
            os_ver  (str)                      : A string that contain specifically the release version
            filters (list[OSReleaseListFilter]): A list of filters to retrieve a unique release

        Returns:
            OSRelease | None: The OS release that matches the provided strings
        """

        if filters is None:
            filters = []

        if os_str is None and os_ver is None:
            return None

        if not isinstance(os, OperatingSystem):
            os_guess = OSOption.guess_os(os)
            if os_guess is None:
                return None

            os = os_guess

        if os_ver is None and os_str is not None:
            os_ver = SoftwareReleaseVersion.search_release_version(os_str)

        # 1: Try to guess release from the provided version if possible
        if os_ver is None:
            OSOption.guess_os_release(os, os_str, None, filters)

        assert os_ver is not None
        candidates = OSOption._guess_os_candidates_by_version(os, os_ver)

        # 2: If no candidates could be retrieved, try to guess release based on the name
        if candidates is None and os_str is not None:
            candidates = os.releases.find_by_name(os_str)

        # 3: Filter candidates until there is only one element remaining, if possible
        res = None
        if candidates is not None and not candidates.is_empty:
            res = candidates.unique(*filters)

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
            os_str  (str | None)               : A string that may contain operating system, edition and optionaly release details
            os_ver  (str | None)               : A software release version string
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
            os = OSOption.guess_os(os_str)

            if os is not None:
                os_rel = OSOption.guess_os_release(
                    os, os_ver or os_str, filters=filters
                )
                os_edition = OSOption.guess_os_edition(os, os_str)

                res = os, os_rel, os_edition

        return res
