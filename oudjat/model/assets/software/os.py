from enum import Enum
from typing import List, Union

from oudjat.utils import ColorPrint
from oudjat.model.assets.computer import ComputerType
from . import Software, SoftwareType, SoftwareRelease, SoftwareReleaseSupport

from .config.windows import WINDOWS_RELEASES

class OSFamily(Enum):
  """ OS family enumeration """
  ANDROID = "android"
  BSD = "bsd"
  LINUX = "linux"
  MAC = "mac"
  UNIX = "unix"
  WINDOWS = "windows"

class WindowsEdition(Enum):
  """ Windows edition enum """
  E   = [ "Enterprise", "Education", "IOT Enterprise" ]
  W   = [ "Home", "Pro", "Pro Education" ]
  IOT = [ "IOT" ]

class OperatingSystem(Software):
  """ A class to describe operating systems """
  
  # ****************************************************************
  # Attributes & Constructors
  
  def __init__(
    self,
    id: Union[int, str],
    name: str,
    label: str,
    os_family: OSFamily,
    computer_type: Union[Union[str, ComputerType], List[Union[str, ComputerType]]],
    editor: Union[str, List[str]] = None,
    description: str = None,
  ):
    """ Constructor """
    
    super().__init__(
      id=id,
      name=name,
      label=label,
      software_type=SoftwareType.OS,
      editor=editor,
      description=description
    )

    if not isinstance(computer_type, list):
      computer_type = [ computer_type ]
      
    self.computer_type = []
    for t in computer_type:
      if not isinstance(t, ComputerType):
        try:
          self.computer_type.append(ComputerType[t.upper()])

        except ValueError as e:
          ColorPrint.red(f"Could not add {t} as computer type")
      
      else:
        self.computer_type.append(t)

    self.os_family = os_family
    
  # ****************************************************************
  # Methods
  
  def get_computer_type(self) -> List[ComputerType]:
    """ Getter for the OS computer type """
    return self.computer_type
  
  def get_os_family(self) -> OSFamily:
    """ Getter for OS family """
    return self.os_family
  

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

      win_sup = SoftwareReleaseSupport(
        active_support=rel["support"],
        end_of_life=rel["eol"],
        edition=rel["edition"]
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
    
  # ****************************************************************
  # Methods
  
  def gen_releases(self) -> None:
    """ Generates Windows releases """
    super().gen_releases("windows-server")

