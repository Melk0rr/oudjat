"""A simple module that lists operating system options."""

from enum import Enum

from oudjat.core.computer.computer_type import ComputerType
from oudjat.core.software.os.os_families import OSFamily

from .windows.windows import MicrosoftOperatingSystem


class OSOption(Enum):
    """An enumeration of OSes."""

    WINDOWS = MicrosoftOperatingSystem(
        msos_id="ms-windows",
        name="Windows",
        label="windows",
        computer_type=ComputerType.WORKSTATION,
        description="Microsoft operating system for workstations",
        tags=["microsoft", "windows"],
    )

    WINDOWSSERVER = MicrosoftOperatingSystem(
        msos_id="ms-windows-server",
        name="Windows Server",
        label="windows-server",
        computer_type=ComputerType.SERVER,
        description="Microsoft operating system for servers",
        tags=["microsoft", "windows"],
    )

    @staticmethod
    def per_family(family: "OSFamily") -> dict[str, "OSOption"]:
        """
        Return a dictionary of OSOption that are bound to the provided OSFamily.

        Args:
            family (OSFamily): The OSFamily the options must be bound to

        Returns:
            dict[str, OSOption]: A dictionary of OSOption bound to the provided family
        """

        return { option.name: option for option in OSOption if option.name in family.options }

