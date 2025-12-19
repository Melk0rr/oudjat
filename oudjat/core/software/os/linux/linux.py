"""
A module to declare some linux editions per distribution.
"""

from enum import Enum

from oudjat.core.software import SoftwareEdition, SoftwareEditionDict


class LinuxEdition(Enum):
    """
    An enumeration of linux editions per distribution.

    Attributes:
        RHEL: Editions related to Red Hat Enterprise Linux
    """

    RHEL = SoftwareEditionDict(
        {"Standard": SoftwareEdition(label="Standard", channel="Standard", pattern=r"[Ss]tandard")}
    )
