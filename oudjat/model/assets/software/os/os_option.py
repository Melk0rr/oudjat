from enum import Enum

from oudjat.model.assets.computer import ComputerType

from . import MicrosoftOperatingSystem


class OSOption(Enum):
    """Agregation of oses"""

    WINDOWS = MicrosoftOperatingSystem(
        id="windows",
        name="Windows",
        label="ms-windows",
        computer_type=ComputerType.WORKSTATION,
        description="Microsoft operating system for workstations",
    )

    WINDOWSSERVER = MicrosoftOperatingSystem(
        id="windows-server",
        name="Windows Server",
        label="ms-windows-server",
        computer_type=ComputerType.SERVER,
        description="Microsoft operating system for servers",
    )

