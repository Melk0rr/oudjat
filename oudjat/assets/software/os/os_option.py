"""A simple module that lists operating system options."""

from enum import Enum

from oudjat.assets.computer.computer_type import ComputerType

from .windows.windows import MicrosoftOperatingSystem


class OSOption(Enum):
    """An enumeration of OSes."""

    WINDOWS = MicrosoftOperatingSystem(
        msos_id="windows",
        name="Windows",
        label="ms-windows",
        computer_type=ComputerType.WORKSTATION,
        description="Microsoft operating system for workstations",
    )

    WINDOWSSERVER = MicrosoftOperatingSystem(
        msos_id="windows-server",
        name="Windows Server",
        label="ms-windows-server",
        computer_type=ComputerType.SERVER,
        description="Microsoft operating system for servers",
    )
