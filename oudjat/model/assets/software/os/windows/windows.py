import re

from enum import Enum
from datetime import datetime
from typing import List, Dict, Union

from oudjat.model.assets.computer import ComputerType
from oudjat.model.assets.software import SoftwareReleaseSupport, SoftwareEdition, SoftwareEditionDict
from oudjat.model.assets.software.os import OperatingSystem, OSRelease, OSFamily

from . import WINDOWS_RELEASES

class MSOSRelease(OSRelease):
  """ A class to handle Microsoft OS releases """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(
    self,
    software: "Software",
    version: Union[int, str],
    release_date: Union[str, datetime],
    release_label: str
  ):
    """ Constructor """
    super().__init__(
      software=software,
      version=version,
      release_date=release_date,
      release_label=release_label
    )
    
    version_split = self.version.split('.')
    self.version_build = self.version.split('.')[-1]
    self.version_main = '.'.join(self.version.split('.')[:-1])

  # ****************************************************************
  # Methods
  
  def get_version_build(self) -> int:
    """ Get the build number from release version """
    return self.version_build
  
  def get_version_main(self) -> str:
    """ Get the version main release number from release version """
    return self.version_main

  def get_name(self) -> str:
    """ Returns a forged name of the release """
    return f"{self.get_software().get_name()} {self.label.split(' ')[0]}"

  def os_info_dict(self) -> Dict:
    """ Returns a dictionary with os infos """
    return {
      **super().os_info_dict(),
      "name": self.get_name(),
      "version_main": self.version_main,
      "version_build": self.version_build
    }

  def to_dict(self) -> Dict:
    """ Converts the current instance into a dictionary """
    base_dict = super().to_dict()
    return {
      **base_dict,
      **self.os_info_dict()
    }


class WindowsEdition(Enum):
  """ Windows edition enum """
  WINDOWS = {
    "Enterprise": SoftwareEdition(label="Enterprise", category="E", pattern=r'Ent[er]{2}prise'),
    "Education": SoftwareEdition(label="Education", category="E", pattern=r'[EÉeé]ducation'),
    "IoT Enterprise": SoftwareEdition(label="IoT Enterprise", category="E", pattern=r'[Ii][Oo][Tt] Ent[er]{2}prise'),
    "Home": SoftwareEdition(label="Home", category="W", pattern=r'[Hh]ome'),
    "Pro": SoftwareEdition(label="Pro", category="W", pattern=r'Pro(?:fession[n]?[ae]l)?'),
    "Pro Education": SoftwareEdition(label="Pro Education", category="W", pattern=r'Pro(?:fession[n]?[ae]l)? [EÉeé]ducation'),
    "IOT": SoftwareEdition(label="IOT", category="IOT", pattern=r'[Ii][Oo][Tt]'),
  }
  WINDOWSSERVER = {
    "Standard": SoftwareEdition(label="Standard", pattern=r'[Ss]tandard'),
    "Datacenter": SoftwareEdition(label="Datacenter", pattern=r'[Dd]atacenter')
  }


class MicrosoftOperatingSystem(OperatingSystem):
  """ A child class of operating system describing Microsoft OSes """

  # ****************************************************************
  # Attributes & Constructors

  VERSION_REG = r'(\d{1,2}\.\d)\W*(\d{4,5})\W*'
  
  def __init__(
    self,
    id: Union[int, str],
    name: str,
    label: str,
    computer_type: Union[Union[str, ComputerType], List[Union[str, ComputerType]]],
    description: str = None,
  ):
    """ Constructor """

    super().__init__(
      id=id,
      name=name,
      label=label,
      computer_type=computer_type,
      description=description,
      editor="Microsoft",
      os_family=OSFamily.WINDOWS
    )

    self.editions = SoftwareEditionDict(**WindowsEdition[self.name.replace(' ', '').upper()].value)

  # ****************************************************************
  # Methods

  def gen_releases(self) -> None:
    """ Generates Windows releases """

    for rel in WINDOWS_RELEASES[self.id]:
      win_rel = self.find_release(rel["releaseLabel"])

      if win_rel is None:
        win_rel = MSOSRelease(
          software=self,
          version=rel["latest"],
          release_date=rel["releaseDate"],
          release_label=rel["releaseLabel"],
        )

      editions = []
      for ctg in rel.get("edition", []):
        editions.extend(win_rel.get_software().get_editions().get_editions_per_ctg(ctg))

      win_sup = SoftwareReleaseSupport(
        active_support=rel["support"],
        end_of_life=rel["eol"],
        long_term_support=rel["lts"],
        edition=editions
      )
      
      self.add_release(win_rel)
      self.releases[win_rel.get_version()][win_rel.get_label()].add_support(win_sup)

  # ****************************************************************
  # Static methods
  
  def get_matching_version(test_str: str) -> str:
    """ Returns a version matching given string """
    res = None
    search = re.search(MicrosoftOperatingSystem.VERSION_REG, test_str)

    if search is not None:
      res = '.'.join([search.group(1), search.group(2)])
      
    return res