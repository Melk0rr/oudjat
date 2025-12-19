"""An OS sub package dedicated to Linux."""

from .config import RHEL_RELEASES
from .linux import LinuxEdition

__all__ = ["RHEL_RELEASES", "LinuxEdition"]

