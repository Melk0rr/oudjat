from typing import List, Dict

from oudjat.model.assets import Asset
from oudjat.model.assets.network import IPv4
from oudjat.model.assets.software import SoftwareRelease, SoftwareType, SoftwareEdition
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
    os: SoftwareRelease = None,
    os_edition: SoftwareEdition = None,
    ip: List[IPv4] = None
  ):
    """ Constructor """
    
    self.id = id
    self.name = name
    
    if not isinstance(os, SoftwareRelease) or os.get_software().get_software_type() != SoftwareType.OS:
      raise ValueError(f"Invalid OS provided for computer {self.name}. Please provide an OS release")
    
    self.os_release = os

    self.os_edition = None

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
    return self.os_release.get_software().get_computer_type()
  
  def get_os_release(self) -> SoftwareRelease:
    """ Getter for the computer operating system """
    return self.os_release
  
  def get_software_list(self) -> List[SoftwareRelease]:
    """ Getter for the computer software release list """
    return self.softwares

  def set_os(self, os: SoftwareRelease, edition: str = None) -> None:
    """ Setter for computer os """
    if os is not None and os.get_software().get_software_type() != SoftwareType.OS:
      raise ValueError(f"Invalid OS provided for computer {self.name}. Please provide an OS release")
    
    self.os = os

    if edition is not None:
      self.os_edition = edition
  
  def is_os_supported(self) -> bool:
    """ Checks if the computer os is supported """
    if self.os is None:
      return False
    
    return self.os_release.is_supported(edition=self.os_edition)
  
  def to_dict(self) -> Dict:
    """ Converts the current instance into a dictionary """
    
    return {
      "id": self.id,
      "computer_type": self.get_computer_type(),
    }
  