"""A module that defines specific OS properties for Windows."""

import re
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Union

from oudjat.assets.computer.computer_type import ComputerType
from oudjat.assets.software import (
    SoftwareEdition,
    SoftwareEditionDict,
    SoftwareReleaseSupport,
)

from ..operating_system import OperatingSystem, OSFamily, OSRelease
from .config.win_rel import WINDOWS_RELEASES

if TYPE_CHECKING:
    from ...software import Software


class MSOSRelease(OSRelease):
    """A class to handle OS releases specific to Microsoft."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        software: "Software",
        version: Union[int, str],
        release_date: Union[str, datetime],
        release_label: str,
    ) -> None:
        """
        Instanciate OS release specific to Microsoft.

        Args:
            software (Software)                : software instance the release is based on
            version (Union[int, str])          : release version
            release_date (Union[str, datetime]): release date
            release_label (str)                : release label
        """

        super().__init__(
            software=software,
            version=version,
            release_date=release_date,
            release_label=release_label,
        )

        version_split = self.version.split(".")
        self.version_build = version_split[-1]
        self.version_main = ".".join(version_split[:-1])

    # ****************************************************************
    # Methods

    def get_version_build(self) -> int:
        """
        Get the build number from release version.

        Returns:
            int: build number of the release
        """

        return self.version_build

    def get_version_main(self) -> str:
        """
        Get the version main release number from release version.

        Returns:
            str: The main version of the software release.
        """

        return self.version_main

    def get_name(self) -> str:
        """
        Return a forged name of the release.

        This method constructs and returns a string that includes the name of the software
        concatenated with the first word from the label. The software name and label are instance variables of this class.

        Returns:
            str: A combined name based on the software's name and part of its label.
        """

        return f"{self.get_software().get_name()} {self.label.split(' ')[0]}"

    def os_info_dict(self) -> Dict:
        """
        Return a dictionary with os infos.

        This method extends the functionality of its parent class to include specific OS information such as name and version numbers, by combining data from both itself and the superclass. The extended dictionary includes 'name', 'version_main', and 'version_build' keys.

        Returns:
            Dict: A dictionary containing OS-specific information including the software name and versions.
        """

        base_dict = super().os_info_dict()  # Assuming superclass has an os_info_dict method
        return {
            **base_dict,
            "name": self.get_name(),
            "version_main": self.version_main,
            "version_build": self.version_build,
        }

    def to_dict(self) -> Dict:
        """
        Convert the current instance into a dictionary.

        This method overrides or extends the standard conversion behavior to include specific class information such as OS name and version numbers.

        Returns:
            Dict: A dictionary representation of the instance including extended OS-related information.
        """

        base_dict = super().to_dict()  # Assuming superclass has a to_dict method
        return {**base_dict, **self.os_info_dict()}


class WindowsEdition(Enum):
    """
    Windows edition enum.

    Tries to handle edition types (E,W,IOT).
    """

    WINDOWS = {
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
    }
    WINDOWSSERVER = {
        "Standard": SoftwareEdition(label="Standard", pattern=r"[Ss]tandard"),
        "Datacenter": SoftwareEdition(label="Datacenter", pattern=r"[Dd]atacenter"),
    }


class MicrosoftOperatingSystem(OperatingSystem):
    """A child class of operating system describing Microsoft OSes."""

    # ****************************************************************
    # Attributes & Constructors

    VERSION_REG = r"(\d{1,2}\.\d)\W*(\d{4,5})\W*"

    def __init__(
        self,
        msos_id: Union[int, str],
        name: str,
        label: str,
        computer_type: Union[ComputerType, List[ComputerType]],
        description: str = None,
    ) -> None:
        """
        Create a new instance of MicrosoftOperatingSystem.

        Initializes a new instance of the MicrosoftOperatingSystem class with the specified parameters.

        Args:
            msos_id (Union[int, str])                               : The identifier for the operating system.
            name (str)                                              : The name of the operating system.
            label (str)                                             : A short label or abbreviation for the operating system.
            computer_type (Union[ComputerType, List[ComputerType]]) : The type(s) of computer compatible with this operating system.
            description (str, optional)                             : A detailed description of the operating system. Defaults to None.
        """

        super().__init__(
            os_id=id,
            name=name,
            label=label,
            computer_type=computer_type,
            description=description,
            editor="Microsoft",
            os_family=OSFamily.WINDOWS,
        )

        self.editions = SoftwareEditionDict(
            **WindowsEdition[self.name.replace(" ", "").upper()].value
        )

    # ****************************************************************
    # Methods

    def gen_releases(self) -> None:
        """
        Generate Windows releases for the Microsoft operating system.

        This method iterates through predefined release data to create or update MSOSRelease instances
        based on the version and label found in the data. It also sets support details for each release.
        """

        for rel in WINDOWS_RELEASES[self.id]:
            win_rel = self.find_release(rel["releaseLabel"])

            if win_rel is None:
                win_rel = MSOSRelease(
                    software=self,
                    version=rel["latest"],
                    release_date=rel["releaseDate"],
                    release_label=rel["releaseLabel"],
                )

            editions = []
            for ctg in rel.get("edition", []):
                editions.extend(win_rel.get_software().get_editions().get_editions_per_ctg(ctg))

            win_sup = SoftwareReleaseSupport(
                active_support=rel["support"],
                end_of_life=rel["eol"],
                long_term_support=rel["lts"],
                edition=editions,
            )

            self.add_release(win_rel)
            self.releases[win_rel.get_version()][win_rel.get_label()].add_support(win_sup)

    # ****************************************************************
    # Static methods

    @staticmethod
    def get_matching_version(test_str: str) -> str:
        """
        Return a version matching the given string.

        This static method uses a regular expression to find and return a version number from the input string.

        Args:
            test_str (str): The string to search for a version match.

        Returns:
            str: A string representing the matched version, or None if no match is found.
        """

        res = None
        search = re.search(MicrosoftOperatingSystem.VERSION_REG, test_str)

        if search is not None:
            res = ".".join([search.group(1), search.group(2)])

        return res
