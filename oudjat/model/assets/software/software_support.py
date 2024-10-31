from datetime import datetime
from typing import List, Dict, Union

from oudjat.utils import date_format_from_flag, DATE_FLAGS, days_diff

from . import SoftwareEditionDict

def soft_date_str(date: datetime) -> str:
  """ Converts a software date into a string """
  soft_date = None
  if date is not None:
    soft_date = date.strftime(date_format_from_flag(DATE_FLAGS))
    
  return soft_date

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