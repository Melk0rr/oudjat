import re

from enum import Enum
from typing import List, Dict, Union, Tuple

from oudjat.utils import ColorPrint
from oudjat.model.assets.computer import ComputerType
from oudjat.model.assets.software import Software, SoftwareType, SoftwareRelease

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
    "pattern": r'[Dd]ebian|[Uu]buntu|[Mm]int|[Nn]ix[Oo][Ss]|(?:[Oo]pen)?[Ss][Uu][Ss][Ee]|[Ff]edora|[Rr](?:ed )?[Hh](?:at )?[Ee](?:nterprise )?[Ll](?:inux)?|[Oo]racle(?: Linux)?'
  }
  MAC = {
    "name": "mac",
    "pattern": r'[Mm][Aa][Cc](?:[Oo][Ss])?'
  }
  WINDOWS = {
    "name": "windows",
    "pattern": r'[Ww]indows(?: [Ss]erver)?'
  }


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

  # ****************************************************************
  # Static methods

  @staticmethod
  def get_matching_os_family(test_str: str) -> str:
    """ Returns the OS family which pattern matches the provided string """
    if test_str is None:
      return None
      
    for f in OSFamily._member_names_:
      search = re.search(OSFamily[f].value.get("pattern"), test_str)
      if search is not None:
        return search.group(0)
  
  @staticmethod
  def get_matching_version(test_str: str) -> str:
    """ Returns a version matching given string """
    raise NotImplementedError(
      "get_matching_version() method must be implemented by the overloading class")


class OSRelease(SoftwareRelease):
  """ Specific software release for OperatingSystem """
  

  # ****************************************************************
  # Methods
  
  def to_dict(self) -> Dict:
    """ Converts the current instance into a dictionary"""
    base_dict = super().to_dict()
    del base_dict["software"]

    return {
      "os": self.get_software(),
      **base_dict
    }