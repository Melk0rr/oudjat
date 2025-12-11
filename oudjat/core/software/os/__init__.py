"""A software sub package that specifically focuses on operating systems."""

from .operating_system import OperatingSystem, OSRelease
from .os_families import OSFamily
from .os_options import OSOption
from .windows import MicrosoftOperatingSystem

__all__ = ["OperatingSystem", "OSFamily", "OSRelease", "OSOption", "MicrosoftOperatingSystem"]
