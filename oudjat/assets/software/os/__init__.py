"""A software sub package that specifically focuses on operating systems."""

from .operating_system import OperatingSystem, OSFamily, OSRelease
from .os_option import OSOption
from .windows import MicrosoftOperatingSystem

__all__ = ["OperatingSystem", "OSFamily", "OSRelease", "OSOption", "MicrosoftOperatingSystem"]
