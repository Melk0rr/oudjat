from typing import Dict, List, Union

from oudjat.model.assets import Asset, AssetType
from oudjat.model.assets.network import IPv4
from oudjat.model.assets.software import (
    SoftwareEdition,
    SoftwareRelease,
    SoftwareReleaseSupport,
)
from oudjat.model.assets.software.os import OSRelease

from . import ComputerType


class Computer(Asset):
    """A common class for computers"""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(
        self,
        id: Union[int, str],
        name: str,
        label: str = None,
        description: str = None,
        computer_type: Union[str, ComputerType] = None,
        os_release: OSRelease = None,
        os_edition: SoftwareEdition = None,
        ip: Union[str, IPv4] = None,
    ):
        """Constructor"""

        super().__init__(
            id=id, name=name, label=label, description=description, asset_type=AssetType.COMPUTER
        )

        self.os_release = None
        self.os_edition = None
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

    def get_id(self) -> str:
        """Getter for the computer id"""
        return self.id

    def get_name(self) -> str:
        """Getter for the computer name"""
        return self.name

    def get_computer_type(self) -> ComputerType:
        """Getter for the current computer type"""
        cpt_type = ComputerType.OTHER
        if self.os_release is not None:
            cpt_type = self.os_release.get_os().get_computer_type()

        return cpt_type

    def get_os_release(self) -> OSRelease:
        """Getter for the computer operating system"""
        return self.os_release

    def get_os_edition(self) -> SoftwareEdition:
        """Getter for OS edition instance"""
        return self.os_edition

    def get_software_list(self) -> List[SoftwareRelease]:
        """Getter for the computer software release list"""
        return self.softwares

    def get_os_support(self) -> List[SoftwareReleaseSupport]:
        """Get support for current computer os release and edition"""
        return self.os_release.get_support_for_edition(str(self.os_edition))

    def set_computer_type(self, cpt_type: Union[str, ComputerType]) -> None:
        """Sets the type of the current computer"""
        if not isinstance(cpt_type, ComputerType):
            cpt_type = ComputerType[cpt_type]

        self.computer_type = cpt_type

    def get_ip(self) -> IPv4:
        """Getter for computer IP address"""
        return self.ip

    def set_ip(self, ip: Union[str, IPv4]) -> None:
        """Sets the current computer ip address"""

        if not isinstance(ip, IPv4):
            ip = IPv4(ip)

        self.ip: IPv4 = ip

    def resolve_ip(self) -> None:
        """Try to resolve ip address"""
        self.ip = IPv4.resolve_from_hostname(hostname=self.label)

    def set_os(self, os_release: OSRelease, edition: SoftwareEdition = None) -> None:
        """Setter for computer os"""
        if not isinstance(os_release, OSRelease):
            raise ValueError(f"Computer.set_os::Invalid OS provided for {self.name}")

        self.os_release = os_release

        if edition is not None:
            if not isinstance(edition, SoftwareEdition):
                raise ValueError(f"Computer.set_os::Invalid edition provided for {self.name}")

            self.os_edition = edition

    def is_os_supported(self) -> bool:
        """Checks if the computer os is supported"""
        if self.os_release is None:
            return False

        return self.os_release.is_supported(str(self.os_edition))

    def to_dict(self) -> Dict:
        """Converts the current instance into a dictionary"""

        asset_dict = super().to_dict()

        # INFO: OS Release informations
        release_dict = self.os_release.to_dict()
        release_dict.pop("is_supported")
        release_dict.pop("software")
        release_dict.pop("support")

        # INFO: OS support information
        os_support_dict = self.get_os_support()[0].to_dict()

        return {
            **asset_dict,
            "computer_type": "-".join([t.name for t in self.get_computer_type()]),
            "os_release": release_dict.pop("name"),
            "os_release_label": release_dict.pop("label"),
            "os_release_full_name": release_dict.pop("full_name"),
            "os_release_version": release_dict.pop("version"),
            "os_release_date": release_dict.pop("release_date"),
            "os_release_main_version": release_dict.pop("version_main"),
            "os_release_build": release_dict.pop("version_build"),
            "os_edition": str(self.os_edition),
            "os_active_support": os_support_dict.pop("active_support"),
            "os_end_of_life": os_support_dict.pop("end_of_life"),
            "os_support_details": os_support_dict.pop("details"),
            "os_has_lts": os_support_dict.pop("lts"),
            **release_dict,
            "is_os_supported": self.is_os_supported(),
        }
