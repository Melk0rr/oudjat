"""A module that defines the Computer asset type."""

from enum import IntEnum
from typing import Any, NamedTuple, TypedDict, override

from oudjat.core import Asset, AssetType
from oudjat.core.network.ip import IP
from oudjat.core.software import (
    SoftwareEdition,
    SoftwareRelease,
    SoftwareReleaseSupport,
)
from oudjat.core.software.os import OSRelease
from oudjat.core.software.os.os_options import OSOption

from .computer_type import ComputerType


class ComputerOSProps(NamedTuple):
    """
    A helper class to properly and conveniently handle computer os attributes types.
    """

    release: "OSRelease | None"
    edition: "SoftwareEdition | None"


class ComputerStatus(IntEnum):
    """
    A simple enumeration of a computer possible statuses.

    Attributes:
        UNKNOWN: The computer status is unknown
        OFF    : The computer is powered off
        ON     : The computer is powered on
        SLEEP  : The computer is in sleep mode
    """

    UNKNOWN = -1
    OFF = 0
    ON = 1
    SLEEP = 2

    @override
    def __str__(self) -> str:
        """
        Convert a computer status into a simple string.

        Returns:
            str: A string representation of a computer status
        """

        return self._name_


class ComputerBaseDict(TypedDict):
    """
    A helper class to properly handle Computer base dictionary attributes.

    Attributes:
        computerType (ComputerType)    : The type of the computer
        computerStatus (ComputerStatus): The status of the computer
    """

    computerType: str
    computerStatus: str
    ip: str | None
    softwares: dict[str, Any]


class Computer(Asset):
    """A common class for computers."""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(
        self,
        computer_id: int | str,
        name: str,
        label: str | None = None,
        description: str | None = None,
        computer_type: "str | ComputerType | None" = None,
        os_release: "OSRelease | None" = None,
        os_edition: "SoftwareEdition | None" = None,
        ip: "str | IP | None" = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new instance of the class.

        This constructor sets up the basic properties and initializes various attributes related to the computer asset including:
        - type
        - operating system
        - IP address
        - software list
        - protection agent
        - etc.

        Args:
            computer_id (int | str)                  : A unique identifier for the computer, which can be either an integer or a string.
            name (str)                               : The name of the computer.
            label (str | None)                       : A short description or tag for the computer.
            description (str | None)                 : A detailed description of the computer and its purpose.
            computer_type (str | ComputerType | None): Specifies the type of the computer, which can be provided either as a string or an instance of ComputerType enum.
            os_release (OSRelease | None)            : The release version of the operating system installed on the computer. Defaults to None.
            os_edition (SoftwareEdition | None)      : The edition of the operating system for the given release. Defaults to None.
            ip (str | IP | None)                     : The IP address assigned to the computer, which can be provided as either a string or an instance of IPv4 class. Defaults to None.
            kwargs (Any)                             : Any further arguments
        """

        super().__init__(
            asset_id=computer_id,
            name=name,
            label=label,
            description=description,
            asset_type=AssetType.COMPUTER,
            **kwargs,
        )

        self._os: "ComputerOSProps" = ComputerOSProps(os_release, os_edition)

        if computer_type is None or (
            isinstance(computer_type, str) and computer_type.upper() not in ComputerType._member_names_
        ):
            computer_type = ComputerType.UNKNOWN

        else:
            computer_type = ComputerType(computer_type)

        self._computer_type: "ComputerType" = computer_type

        self._ip: IP | None = None
        if ip is not None:
            self.ip = IP(ip) if not isinstance(ip, IP) else ip

        self._softwares: dict[str, SoftwareRelease] = {}
        self._protection_agent: SoftwareRelease | None = None
        self._status: "ComputerStatus" = ComputerStatus.UNKNOWN

    # ****************************************************************
    # Methods

    @property
    def computer_type(self) -> "ComputerType":
        """
        Return the computer type associated with the current computer.

        Returns:
            ComputerType | None: the current computer type
        """

        return self._computer_type

    @computer_type.setter
    def computer_type(self, new_computer_type: "ComputerType") -> None:
        """
        Set the computer type of this computer.

        Args:
            new_computer_type (ComputerType): new computer type
        """

        self._computer_type = new_computer_type

    @property
    def status(self) -> "ComputerStatus":
        """
        Return the computer type associated with the current computer.

        Returns:
            ComputerType | None: the current computer type
        """

        return self._status

    @status.setter
    def status(self, new_status: "ComputerStatus") -> None:
        """
        Set the computer type of this computer.

        Args:
            new_status (ComputerStatus): New computer status
        """

        self._status = new_status

    @property
    def os_release(self) -> "OSRelease | None":
        """
        Return the os release of the current computer.

        Returns:
            OSRelease: the os release instance associate with this computer
        """

        return self._os.release

    # TODO: Better / simpler computer_type handling
    @os_release.setter
    def os_release(self, new_os_release: "OSRelease") -> None:
        """
        Set the os release of the current computer instance.

        Args:
            new_os_release (OSRelease): os release instance to set to this computer
        """

        self.computer_type = next(iter(OSOption[new_os_release.os].value.computer_type))
        self._os = ComputerOSProps(new_os_release, self._os.edition)

    @property
    def os_edition(self) -> SoftwareEdition | None:
        """
        Return the os edition of the current computer.

        Returns:
            type and description of the returned object.
        """

        return self._os.edition

    @os_edition.setter
    def os_edition(self, new_edition: SoftwareEdition) -> None:
        """
        Set the os edition of the current computer instance.

        Args:
            new_edition (SoftwareEdition): software edition to set as the os edition for this computer
        """

        self._os = ComputerOSProps(self._os.release, new_edition)

    @property
    def os(self) -> ComputerOSProps:
        """
        Return the os informations for this computer.

        Returns:
            ComputerOSProps: os informations as a ComputerOSProps instance
        """

        return self._os

    @os.setter
    def os(self, new_os: "ComputerOSProps") -> None:
        """
        Set the os informations for the current computer object.

        Args:
            new_os (ComputerOSProps): new os informations represented as a ComputerOSProps instance
        """

        if new_os.release is not None:
            self.computer_type = next(iter(OSOption[new_os.release.os].value.computer_type))

        self._os = new_os

    @property
    def ip(self) -> IP | None:
        """
        Return the current IP address of this computer.

        Returns:
            IPv4 | None: IPv4 instance associated with the current computer instance. Or none if no address is set
        """

        return self._ip

    @ip.setter
    def ip(self, new_ip: "IP") -> None:
        """
        Set a new ip address for this computer.

        Args:
            new_ip (IPv4): new ip address for the current computer instance
        """

        self._ip = new_ip

    @property
    def os_support(self) -> "SoftwareReleaseSupport | None":
        """
        Get support for current computer os release and edition.

        Returns:
            list[SoftwareReleaseSupport]: A list of SoftwareReleaseSupport instances representing the support for the current OS release and edition.
        """

        support = None
        if self._os.release is not None:
            if self._os.edition is not None:
                support = self._os.release.support_channels.get(self._os.edition.channel)

        return support

    @property
    def softwares(self) -> dict[str, "SoftwareRelease"]:
        """
        Return the computer software release dictionary.

        Returns:
            dict[str, SoftwareRelease]: A dictionary of SoftwareRelease instances representing the software installed on the computer.
        """

        return self._softwares

    def set_ip_from_str(self, new_ip_str: str) -> None:
        """
        Set a new ip address for this computer based on a string.

        Args:
            new_ip_str (str): The IPv4 instance representing the IP address of the computer.
        """

        self._ip = IP(new_ip_str)

    def resolve_ip(self) -> None:
        """
        Attempt to resolve the IP address from the hostname.
        """

        resolved_ip: str | None = None
        if self.label is not None:
            resolved_ip = IP.resolve_from_hostname(hostname=self.label)

        if resolved_ip is not None:
            self._ip = IP(resolved_ip)

    def os_supported(self) -> bool:
        """
        Check if the operating system of the computer is supported.

        Returns:
            bool: True if the OS is supported, False otherwise.
        """

        if self._os.release is None:
            return False

        return self._os.release.is_supported(self._os.edition)

    @override
    def __str__(self) -> str:
        """
        Convert the current computer instance into a string.

        Returns:
            str: a string representation of the current instance
        """

        return self.name

    @override
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the current instance into a dictionary representation.

        Returns:
            dict[str, Any]: A dictionary containing information about the computer, including OS release and edition details.
        """

        # OS Release informations
        release_dict = self._os.release.to_dict() if self._os.release is not None else {}
        if "supportChannels" in release_dict:
            del release_dict["supportChannels"]

        edition_dict = self._os.edition.to_dict() if self._os.edition is not None else {}

        # OS support information
        os_support_dict = self.os_support.to_dict() if self.os_support is not None else {}

        base_dict: "ComputerBaseDict" = {
            "computerType": str(self._computer_type),
            "computerStatus": str(self._status),
            "ip": str(self._ip) if self._ip else None,
            "softwares": {sid: s.to_dict() for sid, s in self._softwares.items()}
        }

        return {
            **super().to_dict(),
            **base_dict,
            "osRelease": release_dict,
            "osEdition": edition_dict,
            "osSupport": os_support_dict,
        }
