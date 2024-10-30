import re

from enum import Enum
from datetime import datetime
from typing import List, Dict, Union, Tuple

from oudjat.utils import date_format_from_flag, DATE_FLAGS, days_diff
from oudjat.model.assets import Asset, AssetType
from oudjat.model.vulnerability import CVE_REGEX

def soft_date_str(date: datetime) -> str:
  """ Converts a software date into a string """
  soft_date = None
  if date is not None:
    soft_date = date.strftime(date_format_from_flag(DATE_FLAGS))
    
  return soft_date

class SoftwareType(Enum):
  """ An enumeration to list software types """
  OS = 0
  APPLICATION = 1
  
class SoftwareEdition:
  """ A class to handle software editions """
  
  # ****************************************************************
  # Attributes & Constructors
  
  def __init__(
    self,
    label: str,
    category: str = None,
    pattern: str = None
  ):
    """ Constructor """
    self.label = label
    self.category = category
    self.pattern = pattern
    
  # ****************************************************************
  # Methods

  def get_label(self) -> str:
    """ Getter for edition label """
    return self.label
  
  def get_category(self) -> str:
    """ Getter for edition category """
    return self.category
  
  def get_pattern(self) -> str:
    """ Getter for edition pattern """
    return self.pattern
  

class SoftwareEditionDict(dict):
  """ Software edition dictionary """

  def get_matching_editions(self, label: str) -> List[SoftwareEdition]:
    """ Returns software editions for which the given label match the pattern """
    return [ e for e in self.values() if e.get_pattern() is None or re.match(e.get_pattern(), label) ]
  
  def get_edition_labels(self) -> List[str]:
    """ Returns a list of edition labels """
    return [ e.get_label() for e in self.values() ]
  
  def get_editions_per_ctg(self, category: str) -> "SoftwareEditionDict":
    """ Returns a sub software edition dict based on category value """
    res = { k: v for k, v in self.items() if v.get_category() == category }
    return SoftwareEditionDict(**res)
  
class SoftwareReleaseSupport:
  """ A class to handle software release support concept """
  
  # ****************************************************************
  # Attributes & Constructors
  
  def __init__(
    self,
    active_support: Union[str, datetime] = None,
    end_of_life: Union[str, datetime] = None,
    edition: Union[Dict, SoftwareEditionDict] = None,
    long_term_support: bool = False
  ):
    """ Constructor """

    if edition is not None and not isinstance(edition, SoftwareEditionDict):
      edition = SoftwareEditionDict(**edition)

    self.edition = edition

    # Handling none support values
    if active_support is not None and end_of_life is None:
      end_of_life = active_support

    if active_support is None and end_of_life is not None:
      active_support = end_of_life

    # Datetime convertion
    try:        
      if end_of_life is not None and not isinstance(end_of_life, datetime):
        end_of_life = datetime.strptime(end_of_life, date_format_from_flag(DATE_FLAGS))

      if active_support is not None and not isinstance(active_support, datetime):
        active_support = datetime.strptime(active_support, date_format_from_flag(DATE_FLAGS))

    except ValueError as e:
      raise ValueError(f"Please provide dates with %Y-%m-%d format\n{e}")

    self.active_support = active_support
    self.end_of_life = end_of_life

    self.lts = long_term_support

  # ****************************************************************
  # Methods
  
  def get_edition(self) -> SoftwareEditionDict:
    """ Getter for release edition """
    return self.edition
  
  def get_edition_str(self, join_char: str = ',') -> str:
    """ Returns joined editions """
    return join_char.join(self.edition.get_edition_labels())
  
  def is_ongoing(self) -> bool:
    """ Returns wheither or not the current support is ongoing """
    if self.end_of_life is None:
      return True
    
    return days_diff(self.end_of_life, reverse=True) > 0

  def status(self) -> str:
    """ Returns a string based on current support status """
    return "Ongoing" if self.is_ongoing() else "Retired"

  def support_details(self) -> str:
    """ Returns a string based on the supported status """
    support_days = days_diff(self.end_of_life, reverse=True)
    state = f"{abs(support_days)} days"
    
    if support_days > 0:
      state = f"Ends in {state}"
      
    else:
      state = f"Ended {state} ago"
      
    return state

  def has_long_term_support(self) -> bool:
    """ Returns wheither the release has long term support or not """
    return self.lts

  def supports_edition(self, edition_label: str) -> bool:
    """ Checks if current support concerns the provided edition """
    if edition_label is None:
      return False
    
    return self.edition is None or edition_label in self.edition.get_edition_labels()

  def compare_support_scope(self, edition_labels: Union[str, List[str]], lts: bool = False) -> bool:
    """ Compares current support with given values """
    compare = False
    
    if not isinstance(edition_labels, list):
      edition_labels = [ edition_labels ]
      
    return all([ self.supports_edition(e) for e in edition_labels ]) and lts == self.lts
  
  def to_string(self) -> str:
    """ Converts the current support instance into a string """
    return f"{self.get_edition_str()} ({self.status()}){" - LTS" if self.lts else ''}"
  
  def to_dict(self) -> Dict:
    """ Converts the current support instance into a dict """
    return {
      "edition": self.get_edition_str(),
      "active_support": soft_date_str(self.active_support),
      "end_of_life": soft_date_str(self.end_of_life),
      "status": self.status(),
      "lts": self.lts,
      "details": self.support_details()
    }


class SoftwareReleaseSupportList(list):
  """ A class to manage lists of software releases """

  # ****************************************************************
  # Attributes & Constructors


  # ****************************************************************
  # Methods
  def contains(
    self,
    edition: Union[str, List[str]] = None,
    lts: bool = False,
  ) -> bool:
    """ Check if list contains element matching provided attributes """
    return any([ s.compare_support_scope(edition, lts) for s in self ])

  def get(
    self,
    edition: Union[str, List[str]] = None,
    lts: bool = False,
  ) -> List[SoftwareReleaseSupport]:
    """ Returns releases matching arguments """
    return [ s for s in self if s.compare_support_scope(edition, lts) ]

  def append(self, support: SoftwareReleaseSupport) -> None:
    """ Appends a new support to the list """
    if isinstance(support, SoftwareReleaseSupport):
      super().append(support)


class SoftwareRelease:
  """ A class to describe software releases """
  
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

    self.software = software
    self.version = version
    self.label = release_label

    try:
      if not isinstance(release_date, datetime):
        release_date = datetime.strptime(release_date, date_format_from_flag(DATE_FLAGS))

    except ValueError as e:
      raise ValueError(f"Please provide dates with %Y-%m-%d format\n{e}")

    self.release_date = release_date
    self.support = SoftwareReleaseSupportList()
    self.vulnerabilities = set()

  # ****************************************************************
  # Methods

  def get_software(self) -> "Software":
    """ Getter for release software """
    return self.software
  
  def get_label(self) -> str:
    """ Getter for release label """
    return self.label
  
  def get_version(self) -> Union[int, str]:
    """ Getter for release version """
    return self.version
    
    return days_diff(self.end_of_life, reverse=True) > 0
  
  def is_supported(self, edition: str = None) -> bool:
    """ Checks if the current release has an ongoin support """
    return any([ s.is_ongoing() and (edition is None or s.supports_edition(edition)) for s in self.support ])

  def get_support(self) -> SoftwareReleaseSupportList:
    """ Getter for support list """
    return self.support

  def get_support_for_edition(self, edition: str = None) -> SoftwareReleaseSupportList:
    """ Returns support for given edition """
    if edition is None:
      return None
    
    return [ s.supports_edition(edition) for s in self.support ]
  
  def get_ongoing_support(self) -> List[SoftwareReleaseSupport]:
    """ Returns ongoing support instances """
    return [ s for s in self.support if s.is_ongoing() ]
  
  def get_retired_support(self) -> List[SoftwareReleaseSupport]:
    """ Returns retired support instances """
    return [ s for s in self.support if not s.is_ongoing() ]
  
  def add_support(self, support: SoftwareReleaseSupport) -> None:
    """ Adds a support instance to the current release """
    if (
      isinstance(support, SoftwareReleaseSupport) and 
      not self.support.contains(edition=support.get_edition(), lts=support.has_long_term_support())
    ):
      self.support.append(support)
      
  def has_vulnerability(self, vuln: Union[str, List[str]] = None) -> List[str]:
    """ Check if the release is concerned by any or specific vulnerability """
    if vuln is None:
      return list(self.vulnerabilities)
    
    if not isinstance(vuln, list):
      vuln = [ vuln ]
      
    return [ v in self.vulnerabilities for v in vuln ]
      
  def add_vuln(self, vuln: str) -> None:
    """ Adds a vulnerability to the current release """
    self.vulnerabilities.add(vuln)

  def to_string(self, show_version: bool = False) -> str:
    """ Converts current release to a string """
    name = f"{self.software.get_name()} {self.label or ''}"

    if show_version:
      name = f"{name.strip()}({self.version})"

    return name.strip()

  def to_dict(self) -> Dict:
    """ Converts current release into a dict """
    return {
      "software": self.software.get_name(),
      "label": self.label,
      "full_name": self.to_string(),
      "version": self.version,
      "release_date": soft_date_str(self.release_date),
      "support": ', '.join([ s.to_string() for s in self.support ]),
      "is_supported": self.is_supported(),
    }


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
    self.releases = {}
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
    
  def add_release(self, new_release: SoftwareRelease) -> None:
    """ Adds a release to the list of software releases """
    if isinstance(new_release, SoftwareRelease) and not self.has_release(new_release.get_label()):
      self.releases[new_release.get_label()] = new_release

  def find_release(self, label: str) -> SoftwareRelease:
    """ Finds a release by label """
    return self.releases.get(label, None)

  def has_release(self, label: str) -> bool:
    """ Checks if the current software has a release with the given version """
    return label in self.releases.keys()

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
