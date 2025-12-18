"""An OS sub package dedicated to Windows."""

from .config import WINDOWS_RELEASES, WINDOWS_SERVER_RELEASES
from .windows import MicrosoftOperatingSystem, WindowsEdition

__all__ = ["WINDOWS_RELEASES", "WINDOWS_SERVER_RELEASES", "MicrosoftOperatingSystem", "WindowsEdition"]
