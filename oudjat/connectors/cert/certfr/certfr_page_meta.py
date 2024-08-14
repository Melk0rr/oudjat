import re

from bs4 import BeautifulSoup, element
from typing import List, Dict

class CERTFRPageMeta:
  """ Handles meta table from CERTFR page """
  
  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, meta_section: element):
    """ Constructor """
    self.meta_table = meta_section.find_all("table")[0]
    self.data = None

    self.date_initial: str = None
    self.date_last: str = None
    self.sources: List[str] = None

  # ****************************************************************
  # Methods

  def parse(self) -> None:
    """ Parse meta table """
    meta = {}

    for row in self.meta_table.find_all("tr"):
      cells = row.find_all("td")
      c_name = cells[0].text.strip()
      c_value = cells[-1].text.strip()

      meta[self.clean_str(c_name)] = self.clean_str(c_value)
    
    self.data = meta

  def get_date_initial(self) -> str:
    """ Getter / parser for initial page date """

    if self.data is not None and self.date_initial is None:
      self.date_initial = self.data.get("Date de la première version", None)

    return self.date_initial

  def get_date_last(self) -> str:
    """ Getter / parser for page last change date """
    
    if self.data is not None and self.date_last is None:
      self.date_last = self.data.get("Date de la dernière version", None)

    return self.date_last

  def get_sources(self) -> List[str]:
    """ Getter / parser for page sources """
    
    if self.data is not None and self.sources is None:
      clean_sources = self.data.get("Source(s)", "").split("\n")
      clean_sources = [
        re.sub(r'\s+', ' ', line).strip()
        for line in clean_sources if re.sub(r'\s+', '', line).strip()
      ]

      self.sources = clean_sources

    return self.sources

  def to_dictionary(self) -> Dict:
    """ Converts current instance into a dictionary """
    meta_dict = {}

    if self.data is not None:
      meta_dict = {
        "date_initial": self.get_date_initial(),
        "date_last": self.get_date_last(),
        "sources": self.get_sources()
      }

    return meta_dict

  # ****************************************************************
  # Static methods

  @staticmethod
  def clean_str(str: str) -> str:
    return str.replace("\r", "").strip()
