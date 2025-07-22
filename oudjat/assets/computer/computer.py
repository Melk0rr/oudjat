"""A module that defines the Computer asset type."""

from typing import NamedTuple, override

from oudjat.assets import Asset, AssetType
from oudjat.assets.network.ipv4 import IPv4
from oudjat.assets.software import (
    SoftwareEdition,
    SoftwareRelease,
    SoftwareReleaseSupport,
)
from oudjat.assets.software.os import OSRelease

from .computer_type import ComputerType


class ComputerOSProps(NamedTuple):
    """
    A helper class to properly and conveniently handle computer os attributes types.
    """

    release: OSRelease | None
    edition: SoftwareEdition | None


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
        computer_type: str | ComputerType | None = None,
        os_release: OSRelease | None = None,
        os_edition: SoftwareEdition | None = None,
        ip: str | IPv4 | None = None,
    ) -> None:
        """
        Initialize a new instance of the class.

        This constructor sets up the basic properties and initializes various attributes related to the computer asset including:
        - type
        - operating system
        - release
        - edition
        - IP address
        - software list
        - protection agent
        - etc.

        Args:
            computer_id (Union[int, str])           : A unique identifier for the computer, which can be either an integer or a string.
            name (str)                              : The name of the computer.
            label (str, optional)                   : A short description or tag for the computer.
            description (str, optional)             : A detailed description of the computer and its purpose.
            computer_type (Union[str, ComputerType]): Specifies the type of the computer, which can be provided either as a string or an instance of ComputerType enum.
            os_release (OSRelease, optional)        : The release version of the operating system installed on the computer. Defaults to None.
            os_edition (SoftwareEdition, optional)  : The edition of the operating system for the given release. Defaults to None.
            ip (Union[str, IPv4], optional)         : The IP address assigned to the computer, which can be provided as either a string or an instance of IPv4 class. Defaults to None.
        """

        super().__init__(
            asset_id=computer_id,
            name=name,
            label=label,
            description=description,
            asset_type=AssetType.COMPUTER,
        )

        self._os: ComputerOSProps = ComputerOSProps(os_release, os_edition)

        if os_release is not None:
            self.os = ComputerOSProps(os_release, os_edition)

        self._computer_type: ComputerType | None = None

        self._ip: IPv4 | None = None
        if ip is not None:
            self.ip = IPv4(ip) if not isinstance(ip, IPv4) else ip

        self._softwares: dict[str, SoftwareRelease] = {}
        self._protection_agent: SoftwareRelease | None = None

    # ****************************************************************
    # Methods

    @property
    def computer_type(self) -> ComputerType | None:
        """
        Return the computer type associated with the current computer.

        Returns:
            ComputerType | None: the current computer type
        """

        return self._computer_type

    @computer_type.setter
    def computer_type(self, new_computer_type: ComputerType) -> None:
        """
        Set the computer type of this computer.

        Args:
            new_computer_type (ComputerType): new computer type
        """

        self._computer_type = new_computer_type

    @property
    def os_release(self) -> OSRelease | None:
        """
        Return the os release of the current computer.

        Returns:
            OSRelease: the os release instance associate with this computer
        """

        return self._os.release

    @os_release.setter
    def os_release(self, new_os_release: OSRelease) -> None:
        """
        Set the os release of the current computer instance.

        Args:
            new_os_release (OSRelease): os release instance to set to this computer
        """

        self.computer_type = next(iter(new_os_release.get_os().get_computer_type()))
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
    def os(self, new_os: ComputerOSProps) -> None:
        """
        Set the os informations for the current computer object.

        Args:
            new_os (ComputerOSProps): new os informations represented as a ComputerOSProps instance
        """

        if new_os.release is not None:
            self.computer_type = next(iter(new_os.release.get_os().get_computer_type()))

        self._os = new_os

    @property
    def ip(self) -> IPv4 | None:
        """
        Return the current IP address of this computer.

        Returns:
            IPv4 | None: IPv4 instance associated with the current computer instance. Or none if no address is set
        """

        return self._ip

    @ip.setter
    def ip(self, new_ip: IPv4) -> None:
        """
        Set a new ip address for this computer.

        Args:
            new_ip (IPv4): new ip address for the current computer instance
        """

        self._ip = new_ip

    @property
    def os_support(self) -> list[SoftwareReleaseSupport]:
        """
        Get support for current computer os release and edition.

        Returns:
            List[SoftwareReleaseSupport]: A list of SoftwareReleaseSupport instances representing the support for the current OS release and edition.
        """

        if self._os.release is None:
            return []

        return self._os.release.get_support_for_edition(str(self._os.edition))

    def set_ip_from_str(self, new_ip_str: str) -> None:
        """
        Set a new ip address for this computer based on a string.

        Args:
            new_ip_str (str): The IPv4 instance representing the IP address of the computer.
        """

        self._ip = IPv4(new_ip_str)

    def resolve_ip(self) -> None:
        """
        Attempt to resolve the IP address from the hostname.
        """

        resolved_ip: str | None = None
        if self.label is not None:
            resolved_ip = IPv4.resolve_from_hostname(hostname=self.label)

        if resolved_ip is not None:
            self._ip = IPv4(resolved_ip)

    def get_softwares(self) -> dict[str, SoftwareRelease]:
        """
        Getter for the computer software release list.

        Returns:
            dict[str, SoftwareRelease]: A dictionary of SoftwareRelease instances representing the software installed on the computer.
        """

        return self._softwares

    def is_os_supported(self) -> bool:
        """
        Check if the operating system of the computer is supported.

        Returns:
            bool: True if the OS is supported, False otherwise.
        """

        if self._os.release is None:
            return False

        return self._os.release.is_supported(str(self._os.edition))

    @override
    def to_dict(self) -> dict:
        """
        Convert the current instance into a dictionary representation.

        Returns:
            Dict: A dictionary containing information about the computer, including OS release and edition details.
        """

        asset_dict = super().to_dict()

        # INFO: OS Release informations
        release_dict = {}

        if self._os.release is not None:
            release_dict = self._os.release.to_dict()
            release_dict.pop("is_supported")
            release_dict.pop("software")
            release_dict.pop("support")

        # INFO: OS support information
        os_support_dict = {}
        if len(self.os_support) > 0:
            os_support_dict = self.os_support[0].to_dict()

        return {
            **asset_dict,
            "computer_type": self.computer_type,
            "os_release": release_dict.pop("name", None),
            "os_release_label": release_dict.pop("label", None),
            "os_release_full_name": release_dict.pop("full_name", None),
            "os_release_version": release_dict.pop("version", None),
            "os_release_date": release_dict.pop("release_date", None),
            "os_release_main_version": release_dict.pop("version_main", None),
            "os_release_build": release_dict.pop("version_build", None),
            "os_edition": str(self._os.edition),
            "os_active_support": os_support_dict.pop("active_support", None),
            "os_end_of_life": os_support_dict.pop("end_of_life", None),
            "os_support_details": os_support_dict.pop("details", None),
            "os_has_lts": os_support_dict.pop("lts", False),
            **release_dict,
            "is_os_supported": self.is_os_supported(),
        }
