"""A module that defines specific OS properties for Windows."""

from enum import Enum

from oudjat.core.software import (
    SoftwareEdition,
    SoftwareEditionDict,
)


class WindowsEdition(Enum):
    """
    Windows edition enum.

    Tries to handle edition types (E,W,IOT).
    """

    WINDOWS = SoftwareEditionDict(
        {
            "Enterprise": SoftwareEdition(
                label="Enterprise", channel="E", pattern=r"Ent[er]{2}prise"
            ),
            "Education": SoftwareEdition(
                label="Education", channel="E", pattern=r"[EÉeé]ducation"
            ),
            "IoT Enterprise": SoftwareEdition(
                label="IoT Enterprise", channel="E", pattern=r"[Ii][Oo][Tt] Ent[er]{2}prise"
            ),
            "Home": SoftwareEdition(label="Home", channel="W", pattern=r"[Hh]ome"),
            "Pro": SoftwareEdition(label="Pro", channel="W", pattern=r"Pro(?:fession[n]?[ae]l)?"),
            "Pro Education": SoftwareEdition(
                label="Pro Education",
                channel="W",
                pattern=r"Pro(?:fession[n]?[ae]l)? [EÉeé]ducation",
            ),
            "IOT": SoftwareEdition(label="IOT", channel="IOT", pattern=r"[Ii][Oo][Tt]"),
        }
    )

    # TODO: See how to handle server channels (depends on the release)
    WINDOWSSERVER = SoftwareEditionDict(
        {
            "Enterprise": SoftwareEdition(
                label="Enterprise", channel="LTSC", pattern=r"Ent[er]{2}prise"
            ),
            "Standard": SoftwareEdition(
                label="Standard", channel="LTSC", pattern=r"[Ss]tandard"
            ),
            "Datacenter": SoftwareEdition(
                label="Datacenter", channel="LTSC", pattern=r"[Dd]atacenter"
            ),
        }
    )

    @property
    def editions(self) -> list[SoftwareEdition]:
        """The editions property."""

        return list(self._value_.values())

