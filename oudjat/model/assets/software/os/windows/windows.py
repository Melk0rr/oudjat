from enum import Enum
from typing import List, Union

from oudjat.model.assets.computer import ComputerType
from oudjat.model.assets.software import SoftwareRelease, SoftwareReleaseSupport, SoftwareEdition, SoftwareEditionDict
from oudjat.model.assets.software.os import OperatingSystem, OSFamily

from . import WINDOWS_RELEASES

class MSOSRelease(SoftwareRelease):
  """ A class to handle Microsoft OS releases """

  # ****************************************************************
  # Methods
  
  def get_version_build(self) -> int:
    """ Get the build number from release version """
    return self.version.split('.')[-1]
  
  def get_version_main(self) -> str:
    """ Get the version main release number from release version """
    return '.'.join(self.version.split('.')[:-1])


class WindowsEdition(Enum):
  """ Windows edition enum """
  WINDOWS = {
    "Enterprise": SoftwareEdition(label="Enterprise", category="E", pattern=r'Ent[er]{2}prise'),
    "Education": SoftwareEdition(label="Education", category="E", pattern=r'[EÉeé]ducation'),
    "IoT Enterprise": SoftwareEdition(label="IoT Enterprise", category="E", pattern=r'[Ii][Oo][Tt] Ent[er]{2}prise'),
    "Home": SoftwareEdition(label="Home", category="W", pattern=r'Home'),
    "Pro": SoftwareEdition(label="Pro", category="W", pattern=r'Pro(?:fession[n]?[ae]l)?'),
    "Pro Education": SoftwareEdition(label="Pro Education", category="W", pattern=r'Pro(?:fession[n]?[ae]l)? [EÉeé]ducation'),
    "IOT": SoftwareEdition(label="IOT", category="IOT", pattern=r'[Ii][Oo][Tt]'),
  }
  WINDOWSSERVER = {
    "Standard": SoftwareEdition(label="Standard"),
    "Datacenter": SoftwareEdition(label="Datacenter", pattern=r'Datacenter')
  }


class MicrosoftOperatingSystem(OperatingSystem):
  """ A child class of operating system describing Microsoft OSes """

  # ****************************************************************
  # Attributes & Constructors
  
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
      id=id, name=name,
      label=label,
      computer_type=computer_type,
      description=description,
      editor="Microsoft",
      os_family=OSFamily.WINDOWS
    )

  # ****************************************************************
  # Methods

  def gen_releases(self, os: str = "windows") -> None:
    """ Generates Windows releases """

    for rel in WINDOWS_RELEASES[os]:
      win_rel = self.find_release(rel["releaseLabel"])

      if win_rel is None:
        win_rel = MSOSRelease(
          software=self,
          version=rel["latest"],
          release_date=rel["releaseDate"],
          release_label=rel["releaseLabel"],
        )

      editions = SoftwareEditionDict()
      for ctg in rel.get("edition", []):
        rel_edit = win_rel.get_software().get_editions().get_editions_per_ctg(ctg)
        editions = SoftwareEditionDict(**editions, **rel_edit)

      win_sup = SoftwareReleaseSupport(
        active_support=rel["support"],
        end_of_life=rel["eol"],
        edition=editions
      )
      
      win_rel.add_support(win_sup)
      self.add_release(win_rel)


class Windows(MicrosoftOperatingSystem):
  """ A child class of operating system to describe Microsoft Windows OS for workstation """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(self):
    """ Constructor """
    
    super().__init__(
      id="windows",
      name="Windows",
      label="ms-windows",
      computer_type=ComputerType.WORKSTATION,
      description="Microsoft operating system for workstations"
    )

    self.editions = SoftwareEditionDict(**WindowsEdition.WINDOWS.value)
    
  # ****************************************************************
  # Methods
  
  def gen_releases(self) -> None:
    """ Generates Windows releases """
    super().gen_releases()


class WindowsServer(MicrosoftOperatingSystem):
  """ A child class of operating system to describe Microsoft Windows OS for workstation """
  
  # ****************************************************************
  # Attributes & Constructors

  def __init__(self):
    """ Constructor """
    
    super().__init__(
      id="windows-server",
      name="Windows Server",
      label="ms-windows-server",
      computer_type=ComputerType.SERVER,
      description="Microsoft operating system for servers"
    )

    self.editions = SoftwareEditionDict(**WindowsEdition.WINDOWSSERVER.value)
    
  # ****************************************************************
  # Methods
  
  def gen_releases(self) -> None:
    """ Generates Windows releases """
    super().gen_releases("windows-server")