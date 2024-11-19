from typing import List, Dict

from oudjat.model.assets import Asset, AssetType
from oudjat.model.assets.network import IPv4
from oudjat.model.assets.software import SoftwareRelease, SoftwareType, SoftwareEdition, SoftwareReleaseSupport
from oudjat.model.assets.software.os import OSRelease
from . import ComputerType

class Computer(Asset):
  """ A common class for computers """

  # ****************************************************************
  # Attributes & Constructor

  def __init__(
    self,
    id: str,
    name: str,
    label: str = None,
    description: str = None,
    os_release: OSRelease = None,
    os_edition: SoftwareEdition = None,
    ip: IPv4 = None
  ):
    """ Constructor """
    
    super().__init__(id=id, name=name, label=label, desctiption=description, type=AssetType.COMPUTER)
    
    if not isinstance(os_release, OSRelease):
      raise ValueError(f"Invalid OS provided for computer {self.name}. Please provide an OS release")
    
    self.os_release = os_release
    self.os_edition = os_edition

    self.ip = ip
    self.softwares: List[SoftwareRelease] = []
    
    self.protection_agent = None

  # ****************************************************************
  # Methods

  def get_id(self) -> str:
    """ Getter for the computer id """
    return self.id
  
  def get_name(self) -> str:
    """ Getter for the computer name """
    return self.name
  
  def get_computer_type(self) -> ComputerType:
    """ Getter for the current computer type """
    return self.os_release.get_os().get_computer_type()
  
  def get_os_release(self) -> OSRelease:
    """ Getter for the computer operating system """
    return self.os_release
  
  def get_os_edition(self) -> SoftwareEdition:
    """ Getter for OS edition instance """
    return self.os_edition
  
  def get_software_list(self) -> List[SoftwareRelease]:
    """ Getter for the computer software release list """
    return self.softwares
  
  def get_os_support(self) -> List[SoftwareReleaseSupport]:
    """ Get support for current computer os release and edition """
    return self.os_release.get_support_for_edition(str(self.os_edition))

  def resolve_ip(self) -> None:
    """ Try to resolve ip address """
    self.ip = IPv4.resolve_from_hostname(hostname=self.label)

  def set_os(self, os_release: OSRelease, edition: str = None) -> None:
    """ Setter for computer os """
    if not isinstance(os_release, OSRelease):
      raise ValueError(f"Invalid OS provided for computer {self.name}. Please provide an OS release")
    
    self.os_release = os_release

    if edition is not None:
      self.os_edition = edition
  
  def is_os_supported(self) -> bool:
    """ Checks if the computer os is supported """
    if self.os_release is None:
      return False
    
    return self.os_release.is_supported(str(self.os_edition))
  
  def to_dict(self) -> Dict:
    """ Converts the current instance into a dictionary """
    asset_dict = super().to_dict()
    release_dict = self.os_release.to_dict()
    release_dict.pop("is_supported")
    release_dict.pop("software")
    release_dict.pop("support")
    
    return {
      **asset_dict,
      "computer_type": '-'.join([ t.name for t in self.get_computer_type() ]),
      "os_release": release_dict.pop("name"),
      "os_release_label": release_dict.pop("label"),
      "os_release_full_name": release_dict.pop("full_name"),
      "os_release_version": release_dict.pop("version"),
      "os_release_date": release_dict.pop("release_date"),
      "os_release_main_version": release_dict.pop("version_main"),
      "os_release_build": release_dict.pop("version_build"),
      "os_edition": str(self.os_edition),
      **release_dict,
      "is_os_supported": self.is_os_supported(),
    }
  