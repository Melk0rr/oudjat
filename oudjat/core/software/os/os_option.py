"""A simple module that lists operating system options."""

from enum import Enum

from oudjat.core.computer.computer_type import ComputerType

from .windows.windows import MicrosoftOperatingSystem


class OSOption(Enum):
    """An enumeration of OSes."""

    WINDOWS = MicrosoftOperatingSystem(
        msos_id="ms-windows",
        name="Windows",
        label="windows",
        computer_type=ComputerType.WORKSTATION,
        description="Microsoft operating system for workstations",
        tags=["microsoft", "windows"]
    )

    WINDOWSSERVER = MicrosoftOperatingSystem(
        msos_id="ms-windows-server",
        name="Windows Server",
        label="windows-server",
        computer_type=ComputerType.SERVER,
        description="Microsoft operating system for servers",
        tags=["microsoft", "windows"]
    )

