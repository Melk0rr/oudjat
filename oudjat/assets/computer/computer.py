"""A module that defines the Computer asset type."""

from typing import Dict, List, Union

from oudjat.assets import Asset, AssetType
from oudjat.assets.network.ipv4 import IPv4
from oudjat.assets.software import (
    SoftwareEdition,
    SoftwareRelease,
    SoftwareReleaseSupport,
)
from oudjat.assets.software.os import OSRelease

from .computer_type import ComputerType


class Computer(Asset):
    """A common class for computers."""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(
        self,
        computer_id: Union[int, str],
        name: str,
        label: str = None,
        description: str = None,
        computer_type: Union[str, ComputerType] = None,
        os_release: OSRelease = None,
        os_edition: SoftwareEdition = None,
        ip: Union[str, IPv4] = None,
    ):
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

        self.os_release: OSRelease = None
        self.os_edition: SoftwareEdition = None
        if os_release is not None:
            self.set_os(os_release=os_release, edition=os_edition)

        self.computer_type: ComputerType = None
        self.ip: IPv4 = None

        if ip is not None:
            self.set_ip(ip)

        self.softwares: List[SoftwareRelease] = []
        self.protection_agent = None

    # ****************************************************************
    # Methods

    def get_computer_type(self) -> ComputerType:
        """
        Getter for the current computer type.

        If no specific type is set, it defaults to ComputerType.OTHER. Otherwise, it tries to determine the type based on the os_release.

        Returns:
            ComputerType: The type of the computer.
        """

        cpt_type = ComputerType.OTHER
        if self.os_release is not None:
            cpt_type = self.os_release.get_os().get_computer_type()

        return next(iter(cpt_type))

    def get_os_release(self) -> OSRelease:
        """
        Getter for the computer operating system.

        Returns:
            OSRelease: The OSRelease instance representing the operating system of the computer.
        """

        return self.os_release

    def get_os_edition(self) -> SoftwareEdition:
        """
        Getter for OS edition instance.

        Returns:
            SoftwareEdition: The SoftwareEdition instance representing the edition of the operating system.
        """

        return self.os_edition

    def get_software_list(self) -> List[SoftwareRelease]:
        """
        Getter for the computer software release list.

        Returns:
            List[SoftwareRelease]: A list of SoftwareRelease instances representing the software installed on the computer.
        """

        return self.softwares

    def get_os_support(self) -> List[SoftwareReleaseSupport]:
        """
        Get support for current computer os release and edition.

        Returns:
            List[SoftwareReleaseSupport]: A list of SoftwareReleaseSupport instances representing the support for the current OS release and edition.
        """

        if self.os_release is None:
            return []

        return self.os_release.get_support_for_edition(str(self.os_edition))

    def get_ip(self) -> IPv4:
        """
        Getter for computer IP address.

        Returns:
            IPv4: The IPv4 instance representing the IP address of the computer.
        """

        return self.ip

    def set_computer_type(self, cpt_type: Union[str, ComputerType]) -> None:
        """
        Set the type of the current computer.

        Args:
            cpt_type (Union[str, ComputerType]): The type to be assigned to the computer.
        """

        if not isinstance(cpt_type, ComputerType):
            cpt_type = ComputerType[cpt_type]

        self.computer_type = cpt_type

    def set_ip(self, ip: Union[str, IPv4]) -> None:
        """
        Set the current computer IP address.

        Args:
            ip (Union[str, IPv4]): The IP address to be set for the computer.
        """

        if not isinstance(ip, IPv4):
            ip = IPv4(ip)

        self.ip: IPv4 = ip

    def resolve_ip(self) -> None:
        """
        Attempt to resolve the IP address from the hostname.

        """

        self.ip = IPv4.resolve_from_hostname(hostname=self.label)

    def set_os(self, os_release: OSRelease, edition: SoftwareEdition = None) -> None:
        """
        Setter for the operating system of the computer.

        Args:
            os_release (OSRelease)              : The OSRelease instance representing the operating system release.
            edition (Optional[SoftwareEdition]) : The software edition, optional.

        Raises:
            ValueError: If an invalid OS is provided for the computer.
        """

        if not isinstance(os_release, OSRelease):
            raise ValueError(f"{__class__.__name__}.set_os::Invalid OS provided for {self.name}")

        self.os_release = os_release

        if edition is not None:
            if not isinstance(edition, SoftwareEdition):
                raise ValueError(
                    f"{__class__.__name__}.set_os::Invalid edition provided for {self.name}"
                )

            self.os_edition = edition

    def is_os_supported(self) -> bool:
        """
        Check if the operating system of the computer is supported.

        Returns:
            bool: True if the OS is supported, False otherwise.
        """

        if self.os_release is None:
            return False

        return self.os_release.is_supported(str(self.os_edition))

    def to_dict(self) -> Dict:
        """
        Convert the current instance into a dictionary representation.

        Returns:
            Dict: A dictionary containing information about the computer, including OS release and edition details.
        """

        asset_dict = super().to_dict()

        # INFO: OS Release informations
        release_dict = {}

        if self.os_release is not None:
            release_dict = self.os_release.to_dict()
            release_dict.pop("is_supported")
            release_dict.pop("software")
            release_dict.pop("support")

        # INFO: OS support information
        os_support_dict = {}
        if len(self.get_os_support()) > 0:
            os_support_dict = self.get_os_support()[0].to_dict()

        return {
            **asset_dict,
            "computer_type": self.get_computer_type(),
            "os_release": release_dict.pop("name", None),
            "os_release_label": release_dict.pop("label", None),
            "os_release_full_name": release_dict.pop("full_name", None),
            "os_release_version": release_dict.pop("version", None),
            "os_release_date": release_dict.pop("release_date", None),
            "os_release_main_version": release_dict.pop("version_main", None),
            "os_release_build": release_dict.pop("version_build", None),
            "os_edition": str(self.os_edition),
            "os_active_support": os_support_dict.pop("active_support", None),
            "os_end_of_life": os_support_dict.pop("end_of_life", None),
            "os_support_details": os_support_dict.pop("details", None),
            "os_has_lts": os_support_dict.pop("lts", False),
            **release_dict,
            "is_os_supported": self.is_os_supported(),
        }
