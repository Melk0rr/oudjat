"""An OS sub package dedicated to Windows."""

from .config.releases import WINDOWS_RELEASES
from .windows import MicrosoftOperatingSystem, WindowsEdition

__all__ = ["WINDOWS_RELEASES", "MicrosoftOperatingSystem", "WindowsEdition"]
