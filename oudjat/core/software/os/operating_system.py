"""A module defining operating system behavior."""

from datetime import datetime
from typing import TYPE_CHECKING, Any, override

from oudjat.utils import Context

from ..software import Software, SoftwareType
from ..software_release import SoftwareRelease
from .os_families import OSFamily

if TYPE_CHECKING:
    from oudjat.core.computer.computer_type import ComputerType


class OSRelease(SoftwareRelease):
    """Specific software release for OperatingSystem."""

    # ****************************************************************
    # Constructor & Attributes

    def __init__(
        self,
        release_id: str,
        name: str,
        os_name: str,
        version: int | str,
        release_date: str | datetime,
        release_label: str | None = None,
    ) -> None:
        """
        Instanciate OS release specific to Microsoft.

        Args:
            release_id (str)             : The ID of the release
            name (str)                   : The name of the release
            os_name (Software)           : Software instance the release is based on
            version (int | str)          : Release version
            release_date (str | datetime): Release date
            release_label (str)          : Release label
        """

        super().__init__(
            release_id=release_id,
            name=name,
            software_name=os_name,
            version=version,
            release_date=release_date,
            release_label=release_label,
        )

    # ****************************************************************
    # Methods

    @property
    def os(self) -> str:
        """
        Return the operating system instance tide to the current release.

        Returns:
            OperatingSystem: operating system instance of the current release
        """

        return self._software

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary.

        Returns:
            dict[str, Any]: A dictionary representation of the current instance
        """

        base_dict = super().to_dict()
        os_name = base_dict.pop("software")

        return {"os": os_name, **base_dict}


class OperatingSystem(Software[OSRelease]):
    """A class to describe operating systems."""

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        os_id: int | str,
        name: str,
        label: str,
        os_family: "OSFamily",
        computer_type: "ComputerType | list[ComputerType]",
        editor: str | list[str] | None = None,
        description: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Return a new instance of OperatingSystem.

        Args:
            os_id (int | str)                                : OS unique ID
            name (str)                                       : The name of the operating system
            label (str)                                      : A short string to labelize the os
            os_family (OSFamily)                             : Family of operating system, usually (Linux, MAC, Windows)
            computer_type (ComputerType | list[ComputerType]): The type(s) of computer the OS is tide to
            editor (str | list[str])                         : The editor in charge of the OS maintenance and/or development
            description (str)                                : A string to describe the OS
            **kwargs (Any)                                   : Any additional arguments that will be passed to parent class
        """

        super().__init__(
            software_id=os_id,
            name=name,
            label=label,
            software_type=SoftwareType.OS,
            editor=editor,
            description=description,
            **kwargs,
        )

        if not isinstance(computer_type, list):
            computer_type = [computer_type]

        self._computer_type: list["ComputerType"] = computer_type
        self._os_family: "OSFamily" = os_family

    # ****************************************************************
    # Methods

    @property
    def computer_type(self) -> list["ComputerType"]:
        """
        Return the computer types related to the current OS.

        Returns:
            list[ComputerType]: the list of computer types as ComputerType enumeration elements
        """

        return self._computer_type

    @property
    def os_family(self) -> "OSFamily":
        """
        Return the OS family of the current OS.

        Returns:
            OSFamily: the OS family represented by an OSFamily enumeration element
        """

        return self._os_family

    def gen_releases(self) -> None:
        """
        Generate the list of releases of the current OS.

        It must be overwritten by the classes inheriting OperatingSystem
        """

        raise NotImplementedError(
            f"{Context()}::Method must be implemented by the overloading class"
        )

    @override
    def to_dict(self) -> dict[str, Any]:
        return {
            **super().to_dict(),
            "osFamily": self._os_family,
            "computerTypes": self._computer_type,
        }
