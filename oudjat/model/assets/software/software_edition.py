import re

from typing import List

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
  
  def match_str(self, test_str: str) -> bool:
    """ Checks if provided string matches edition pattern """
    return self.pattern is None or re.match(self.pattern, test_str)
  

class SoftwareEditionDict(dict):
  """ Software edition dictionary """

  def get_matching_editions(self, label: str) -> List[SoftwareEdition]:
    """ Returns software editions for which the given label match the pattern """
    return [ e for e in self.values() if e.match_str(label) ]
  
  def get_edition_labels(self) -> List[str]:
    """ Returns a list of edition labels """
    return [ e.get_label() for e in self.values() ]
  
  def get_editions_per_ctg(self, category: str) -> "SoftwareEditionDict":
    """ Returns a sub software edition dict based on category value """
    res = { k: v for k, v in self.items() if v.get_category() == category }
    return SoftwareEditionDict(**res)