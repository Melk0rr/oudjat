"""A module that defines specific OS properties for Windows."""

import re
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


class MSOSRelease(OSRelease):
    """A class to handle OS releases specific to Microsoft."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        os_name: str,
        version: int | str,
        release_date: str | datetime,
        release_label: str,
    ) -> None:
        """
        Instanciate OS release specific to Microsoft.

        Args:
            os_name (Software)           : Software instance the release is based on
            version (int | str)          : Release version
            release_date (str | datetime): Release date
            release_label (str)          : Release label
        """

        super().__init__(
            software_name=os_name,
            version=version,
            release_date=release_date,
            release_label=release_label,
        )

    # ****************************************************************
    # Methods

    @property
    @override
    def name(self) -> str:
        """
        Return a forged name of the release.

        This method constructs and returns a string that includes the name of the software
        concatenated with the first word from the label. The software name and label are instance variables of this class.

        Returns:
            str: A combined name based on the software's name and part of its label.
        """

        return f"{self.software} {(self.label or "").split(' ')[0]}"

    def _os_dict(self) -> dict[str, Any]:
        """
        Return a dictionary with os infos.

        This method extends the functionality of its parent class to include specific OS information such as name and version numbers, by combining data from both itself and the superclass. The extended dictionary includes 'name', 'version_main', and 'version_build' keys.

        Returns:
            dict[str, Any]: A dictionary containing OS-specific information including the software name and versions.
        """

        base_dict = super()._software_dict()  # Assuming superclass has an os_info_dict method
        return {
            **base_dict,
            "name": self.name,
        }

    @override
    def to_dict(self) -> dict:
        """
        Convert the current instance into a dictionary.

        This method overrides or extends the standard conversion behavior to include specific class information such as OS name and version numbers.

        Returns:
            Dict: A dictionary representation of the instance including extended OS-related information.
        """

        base_dict = super().to_dict()  # Assuming superclass has a to_dict method
        return {**base_dict, **self._os_dict()}


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

    WINDOWSSERVER = SoftwareEditionDict(
        {
            "Standard": SoftwareEdition(
                label="Standard", channel="Standard", pattern=r"[Ss]tandard"
            ),
            "Datacenter": SoftwareEdition(
                label="Datacenter", channel="Standard", pattern=r"[Dd]atacenter"
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
        """

        super().__init__(
            os_id=msos_id,
            name=name,
            label=label,
            computer_type=computer_type,
            description=description,
            editor="Microsoft",
            os_family=OSFamily.WINDOWS,
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
                win_rel = MSOSRelease(
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

