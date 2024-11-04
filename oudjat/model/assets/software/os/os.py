import re

from enum import Enum
from typing import List, Union, Tuple

from oudjat.utils import ColorPrint
from oudjat.model.assets.computer import ComputerType
from oudjat.model.assets.software import Software, SoftwareType

class OSFamily(Enum):
  """ OS family enumeration """
  ANDROID = {
    "name": "android",
    "pattern": r'[Aa]ndroid|[Aa][Oo][Ss][Pp]|[Gg]raphene[Oo][Ss]|[Ll]ineage[Oo][Ss]|\/e\/[Oo][Ss]|[Cc]alyx[Oo][Ss]'
  }
  BSD = {
    "name": "bsd",
    "pattern": r'[Bb][Ss][Dd]'
  }
  LINUX = {
    "name": "linux",
    "pattern": r'[Dd]ebian|[Uu]buntu|[Mm]int|[Nn]ix[Oo][Ss]|[Aa]rch|(?:[Oo]pen)?[Ss][Uu][Ss][Ee]|[Ff]edora|[Rr](?:ed )?[Hh](?:at )?[Ee](?:nterprise )?[Ll](?:inux)?|[Oo]racle(?: Linux)?'
  }
  MAC = {
    "name": "mac",
    "pattern": r'[Mm][Aa][Cc](?:[Oo][Ss])?'
  }
  WINDOWS = {
    "name": "windows",
    "pattern": r'[Ww]indows(?: [Ss]erver)?'
  }

def get_matching_os_family(test_str: str) -> Tuple[str, OSFamily]:
  """ Returns the OS family which pattern matches the provided string """
  for f in OSFamily._member_names_:
    if re.match(OSFamily[f].value.get("pattern"), test_str):
      return (
        re.search(OSFamily[f].value.get("pattern"), test_str).group(0),
        OSFamily[f]
      )

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

        except ValueError:
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

  def gen_releases(self) -> None:
    """ Method to generate releases """
    raise NotImplementedError(
      "gen_releases() method must be implemented by the overloading class")
  
