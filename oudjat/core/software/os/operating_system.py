"""A module defining operating system behavior."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, override

from ..software import Software, SoftwareType
from ..software_release import SoftwareRelease, SoftwareReleaseList

if TYPE_CHECKING:
    from oudjat.core.computer.computer_type import ComputerType


type OSReleaseList = "SoftwareReleaseList[OSRelease]"
type OSReleaseListFilter = Callable[["OSReleaseList"], "OSReleaseList"]
type OSComputerTypeParam = "str | list[str] | ComputerType | list[ComputerType]"


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
        os_family: "str",
        editor: str | list[str] | None = None,
        description: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Return a new instance of OperatingSystem.

        Args:
            os_id         (int | str)          : OS unique ID
            name          (str)                : The name of the operating system
            label         (str)                : A short string to labelize the os
            os_family     (str)                : Family of operating system, usually (Linux, MAC, Windows)
            computer_type (OSComputerTypeParam): The type(s) of computer the OS is tide to
            editor        (str | list[str])    : The editor in charge of the OS maintenance and/or development
            description   (str)                : A string to describe the OS
            **kwargs      (Any)                : Any additional arguments that will be passed to parent class
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

        self._os_family: str = os_family

    # ****************************************************************
    # Methods

    @property
    def os_family(self) -> "str":
        """
        Return the OS family of the current OS.

        Returns:
            str: the OS family represented by a string
        """

        return self._os_family

    @override
    def to_dict(self) -> dict[str, Any]:
        return {
            **super().to_dict(),
            "osFamily": self._os_family,
        }

    # ****************************************************************
    # Static methods

