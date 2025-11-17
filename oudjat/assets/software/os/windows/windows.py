"""A module that defines specific OS properties for Windows."""

import re
from datetime import datetime
from enum import Enum
from typing import Any, override

from oudjat.assets.computer.computer_type import ComputerType
from oudjat.assets.software import (
    SoftwareEdition,
    SoftwareEditionDict,
    SoftwareReleaseSupport,
)

from ..operating_system import OperatingSystem, OSFamily, OSRelease
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

        return f"{self.software} {self.label.split(' ')[0]}"

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

    WINDOWS = SoftwareEditionDict({
        "Enterprise": SoftwareEdition(label="Enterprise", category="E", pattern=r"Ent[er]{2}prise"),
        "Education": SoftwareEdition(label="Education", category="E", pattern=r"[EÉeé]ducation"),
        "IoT Enterprise": SoftwareEdition(
            label="IoT Enterprise", category="E", pattern=r"[Ii][Oo][Tt] Ent[er]{2}prise"
        ),
        "Home": SoftwareEdition(label="Home", category="W", pattern=r"[Hh]ome"),
        "Pro": SoftwareEdition(label="Pro", category="W", pattern=r"Pro(?:fession[n]?[ae]l)?"),
        "Pro Education": SoftwareEdition(
            label="Pro Education", category="W", pattern=r"Pro(?:fession[n]?[ae]l)? [EÉeé]ducation"
        ),
        "IOT": SoftwareEdition(label="IOT", category="IOT", pattern=r"[Ii][Oo][Tt]"),
    })

    WINDOWSSERVER = SoftwareEditionDict({
        "Standard": SoftwareEdition(label="Standard", pattern=r"[Ss]tandard"),
        "Datacenter": SoftwareEdition(label="Datacenter", pattern=r"[Dd]atacenter"),
    })

    @property
    def editions(self) -> list[SoftwareEdition]:
        """The editions property."""

        return list(self._value_.values())


class MicrosoftOperatingSystem(OperatingSystem):
    """A child class of operating system describing Microsoft OSes."""

    # ****************************************************************
    # Attributes & Constructors

    VERSION_REG: str = r"(\d{1,2}\.\d)\W*(\d{4,5})\W*"

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

        # TODO: Use NamedTuple to handle releases types properly or convert to JSON
        for rel in WINDOWS_RELEASES[f"{self._label}"]:
            win_rel = self.find_release(rel.release_label)

            if win_rel is None:
                win_rel = MSOSRelease(
                    os_name=self.name,
                    version=rel.latest,
                    release_date=rel.release_date,
                    release_label=rel.release_label,
                )

            win_sup: "SoftwareReleaseSupport" = SoftwareReleaseSupport(
                active_support=rel.support,
                end_of_life=rel.eol,
                long_term_support=rel.lts,
                edition=self._editions.filter_by_category(rel.edition),
            )

            self.add_release(win_rel)
            self.releases[win_rel.key].add_support(win_sup)

    # ****************************************************************
    # Static methods

    @staticmethod
    @override
    def find_version_in_str(search_str: str) -> str | None:
        """
        Try to find a version in the provided string based on the class VERSION_REG.

        This static method uses a regular expression to find and return a version number from the input string.

        Args:
            search_str (str): The string to search for a version match.

        Returns:
            str: A string representing the matched version, or None if no match is found.
        """

        search = re.search(MicrosoftOperatingSystem.VERSION_REG, search_str)
        return search is not None and ".".join([search.group(1), search.group(2)]) or None

