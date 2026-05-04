"""A module defining operating system behavior."""

from typing import TYPE_CHECKING, Any, Callable, TypeAlias, override

from ..software import Software, SoftwareType
from ..software_release import SoftwareRelease
from .os_families import OSFamily

if TYPE_CHECKING:
    from oudjat.core.computer.computer_type import ComputerType

    from ..software_release import SoftwareReleaseList

OSReleaseList: TypeAlias = "SoftwareReleaseList[OSRelease]"
OSReleaseListFilter: TypeAlias = Callable[["OSReleaseList"], "OSReleaseList"]

class OSRelease(SoftwareRelease):
    """Specific software release for OperatingSystem."""

    # ****************************************************************
    # Constructor & Attributes

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

    @override
    def to_dict(self) -> dict[str, Any]:
        return {
            **super().to_dict(),
            "osFamily": self._os_family,
            "computerTypes": self._computer_type,
        }

    # ****************************************************************
    # Static methods

    @staticmethod
    def os_family_by_name(os_family_name: str) -> "OSFamily":
        """
        Return an OSFamily based on its name.

        Args:
            os_family_name (str): The name of the supposed OSFamily

        Returns:
            OSFamily: The OSFamily enum element based on the provided name
        """

        return OSFamily(os_family_name.upper())
