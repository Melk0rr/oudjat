"""A simple module that lists operating system options."""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from oudjat.core.computer.computer_type import ComputerType

from ..software_release import SoftwareReleaseImportDict
from .linux import RHEL_RELEASES, LinuxEdition
from .operating_system import OperatingSystem, OSRelease
from .os_families import OSFamily
from .windows import WINDOWS_RELEASES, WINDOWS_SERVER_RELEASES, WindowsEdition


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
    releases: "SoftwareReleaseImportDict"
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
            "editions": LinuxEdition.RHEL.value,
            "tags": ["linux-distribution", "red-hat"],
        },
        releases=RHEL_RELEASES,
    )

    WINDOWS = OSOptionProps(
        cls=OperatingSystem,
        attributes={
            "os_id": "ms-windows",
            "name": "Windows",
            "label": "windows",
            "editor": "Microsoft Corporation",
            "os_family": OSFamily.WINDOWS,
            "computer_type": ComputerType.WORKSTATION,
            "description": "Microsoft Windows is the operating system developed by Microsoft to run on workstations",
            "editions": WindowsEdition.WINDOWS.value,
            "tags": ["microsoft", "windows"],
        },
        releases=WINDOWS_RELEASES,
    )

    WINDOWSSERVER = OSOptionProps(
        cls=OperatingSystem,
        attributes={
            "os_id": "ms-windows-server",
            "name": "Windows Server",
            "label": "windows-server",
            "editor": "Microsoft Corporation",
            "os_family": OSFamily.WINDOWS,
            "computer_type": ComputerType.SERVER,
            "description": "Microsoft Windows is the operating system developed by Microsoft to run on servers",
            "editions": WindowsEdition.WINDOWSSERVER.value,
            "tags": ["microsoft", "windows"],
        },
        releases=WINDOWS_SERVER_RELEASES,
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

    @property
    def releases(self) -> "SoftwareReleaseImportDict":
        """
        Return the releases associated with the option.

        Returns:
            OSReleaseImportDict: The dictionary of releases of this option
        """

        return self._value_.releases

    def __call__(self) -> "OperatingSystem":
        """
        Return the operating system of the option by calling it.

        Returns:
            OperatingSystem: The operating system that corresponds to the option
        """

        if self._value_.instance is None:
            self._value_.instance = self._value_.cls(**self.attributes)
            self._value_.instance.releases = OSRelease.gen_releases(self.releases)

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

        return {option.name: option for option in OSOption if option.name in family.names}
