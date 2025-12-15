"""A module that defines specific OS properties for Windows."""

from datetime import datetime
from enum import Enum
from typing import Any, override

from oudjat.core.computer.computer_type import ComputerType
from oudjat.core.software import (
    SoftwareEdition,
    SoftwareEditionDict,
    SoftwareReleaseSupport,
)
from oudjat.core.software.software_release_version import SoftwareReleaseVersion

from ..operating_system import OperatingSystem, OSRelease
from ..os_families import OSFamily
from .config.releases import WINDOWS_RELEASES


class WindowsEdition(Enum):
    """
    Windows edition enum.

    Tries to handle edition types (E,W,IOT).
    """

    WINDOWS = SoftwareEditionDict(
        {
            "Enterprise": SoftwareEdition(
                label="Enterprise", channel="E", pattern=r"Ent[er]{2}prise"
            ),
            "Education": SoftwareEdition(
                label="Education", channel="E", pattern=r"[EÉeé]ducation"
            ),
            "IoT Enterprise": SoftwareEdition(
                label="IoT Enterprise", channel="E", pattern=r"[Ii][Oo][Tt] Ent[er]{2}prise"
            ),
            "Home": SoftwareEdition(label="Home", channel="W", pattern=r"[Hh]ome"),
            "Pro": SoftwareEdition(label="Pro", channel="W", pattern=r"Pro(?:fession[n]?[ae]l)?"),
            "Pro Education": SoftwareEdition(
                label="Pro Education",
                channel="W",
                pattern=r"Pro(?:fession[n]?[ae]l)? [EÉeé]ducation",
            ),
            "IOT": SoftwareEdition(label="IOT", channel="IOT", pattern=r"[Ii][Oo][Tt]"),
        }
    )

    # TODO: See how to handle server channels (depends on the release)
    WINDOWSSERVER = SoftwareEditionDict(
        {
            "Standard": SoftwareEdition(
                label="Standard", channel="LTSC", pattern=r"[Ss]tandard"
            ),
            "Datacenter": SoftwareEdition(
                label="Datacenter", channel="LTSC", pattern=r"[Dd]atacenter"
            ),
        }
    )

    @property
    def editions(self) -> list[SoftwareEdition]:
        """The editions property."""

        return list(self._value_.values())


class MicrosoftOperatingSystem(OperatingSystem):
    """A child class of operating system describing Microsoft OSes."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        msos_id: int | str,
        name: str,
        label: str,
        computer_type: "ComputerType | list[ComputerType]",
        description: str | None = None,
        **kwargs: Any
    ) -> None:
        """
        Create a new instance of MicrosoftOperatingSystem.

        Initializes a new instance of the MicrosoftOperatingSystem class with the specified parameters.

        Args:
            msos_id (int | str)                              : The identifier for the operating system.
            name (str)                                       : The name of the operating system.
            label (str)                                      : A short label or abbreviation for the operating system.
            computer_type (ComputerType | list[ComputerType]): The type(s) of computer compatible with this operating system.
            description (str | None)                         : A detailed description of the operating system. Defaults to None.
            **kwargs (Any)                                   : Any additional arguments that will be passed to parent class
        """

        super().__init__(
            os_id=msos_id,
            name=name,
            label=label,
            computer_type=computer_type,
            description=description,
            editor="Microsoft",
            os_family=OSFamily.WINDOWS,
            **kwargs
        )

        self._editions: "SoftwareEditionDict" = SoftwareEditionDict(
            **WindowsEdition[self._name.replace(" ", "").upper()].value
        )

    # ****************************************************************
    # Methods

    @override
    def gen_releases(self) -> None:
        """
        Generate Windows releases for the Microsoft operating system.

        This method iterates through predefined release data to create or update MSOSRelease instances
        based on the version and label found in the data. It also sets support details for each release.
        """

        releases = WINDOWS_RELEASES[f"{self._label}"]
        for version, version_dict in releases.items():
            win_rel = self.releases.get(version, None)

            if win_rel is None:
                win_rel = OSRelease(
                    os_name=self.name,
                    version=version,
                    release_date=version_dict["releaseDate"],
                    release_label=version_dict["releaseLabel"],
                )

                win_rel.latest_version = SoftwareReleaseVersion(version_dict["latest"])
                win_rel.add_custom_attr("link", version_dict["link"])

            self.add_release(win_rel)

            for channel, support_dict in version_dict["channels"].items():
                win_sup: "SoftwareReleaseSupport" = SoftwareReleaseSupport(
                    channel=channel,
                    active_support=support_dict["activeSupport"],
                    security_support=support_dict["securitySupport"],
                    extended_security_support=support_dict["extendedSecuritySupport"],
                    long_term_support=support_dict["lts"],
                )

                self.releases[version].add_support(channel, win_sup)


    # ****************************************************************
    # Static methods

