from enum import Enum
from datetime import datetime
from typing import List, Dict, Union

from oudjat.utils import date_format_from_flag, DATE_FLAGS, days_diff
from oudjat.model.assets import Asset, AssetType
from oudjat.model.vulnerability import CVE_REGEX

from . import SoftwareRelease, SoftwareReleaseDict, SoftwareEditionDict

class SoftwareType(Enum):
  """ An enumeration to list software types """
  OS = 0
  APPLICATION = 1
  

class Software(Asset):
  """ A class to describe softwares """
  
  # ****************************************************************
  # Attributes & Constructors
  
  def __init__(
    self,
    id: Union[int, str],
    name: str,
    label: str,
    software_type: SoftwareType = SoftwareType.APPLICATION,
    editor: Union[str, List[str]] = None,
    description: str = None,
  ):
    """ Constructor """
    super().__init__(id=id, name=name, label=label, type=AssetType.SOFTWARE, desctiption=description)
    
    self.editor = editor
    self.type = software_type
    self.releases = SoftwareReleaseDict()
    self.editions = SoftwareEditionDict()

  # ****************************************************************
  # Methods
  
  def get_editor(self) -> str:
    """ Getter for software editor """
    return self.editor
  
  def get_releases(self) -> Dict[Union[int, str], SoftwareRelease]:
    """ Getter for software releases """
    return self.releases

  def get_software_type(self) -> SoftwareType:
    """ Getter for software type """
    return self.type

  def get_editions(self) -> SoftwareEditionDict:
    """ Getter for software editions """
    return self.editions

  def set_editor(self, editor: Union[str, List[str]]) -> None:
    """ Setter for software editor """
    self.editor = editor
    
  def has_release(self, rel_ver: str, rel_label: str) -> bool:
    """ Checks if the current software has a release with the given version """
    return self.releases.find_rel(rel_ver, rel_label) is not None

  def add_release(self, new_release: SoftwareRelease) -> None:
    """ Adds a release to the list of software releases """
    if not isinstance(new_release, SoftwareRelease):
      return

    new_rel_ver = new_release.get_version()
    
    if new_rel_ver not in self.releases.keys():
      self.releases[new_rel_ver] = SoftwareReleaseDict()

    self.releases[new_rel_ver][new_release.get_label()] = new_release

  def find_release(self, rel_ver: str, rel_label: str = None) -> SoftwareRelease:
    """ Finds a release by label """
    return self.releases.find_rel(rel_ver, rel_label)

  def retired_releases(self) -> List[SoftwareRelease]:
    """ Gets a list of retired releases """
    return [ r.to_string() for r in self.releases.values() if not r.is_supported() ]

  def supported_releases(self) -> List[SoftwareRelease]:
    """ Gets a list of retired releases """
    return [ r.to_string() for r in self.releases.values() if r.is_supported() ]
  
  def to_dict(self) -> Dict:
    """ Converts the current instance into a dict """
    base_dict = super().to_dict()
    return {
      **base_dict,
      "editor": self.editor,
      "releases": ','.join([ r.to_string() for r in self.releases ]),
      "supported_releases": ','.join(self.supported_releases()),
      "retired_releases": ','.join(self.retired_releases())
    }
