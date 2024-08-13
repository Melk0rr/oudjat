import re

from bs4 import BeautifulSoup, element
from typing import List, Dict, Set, Union

from oudjat.model.cve import CVE, CVE_REGEX
from oudjat.connectors.cert.risk_types import RiskTypes

URL_REGEX = r'http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

class CERTFRPageContent:
  """ Handles content section from CERTFR page """
  
  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, content_section: element, page: "CERTFRPage"):
    """ Constructor """
    self.page = page
    self.content = content_section
    self.data = None

    self.description = None
    self.risks: Set[str] = set()
    self.cves: Dict["CVE"] = {}
    self.documentations: List[str] = []
    self.affected_products: List[str] = []

  # ****************************************************************
  # Methods

  def get_risks(self, short: bool = True) -> Set["RiskTypes"]:
    """ Getter / parser for the list of risks """
    
    if len(self.risks) == 0:
      for risk in list(RiskTypes):
        if risk.value.lower() in [ r.lower() for r in self.content["risks"] ]:
          self.risks.add(risk)

    return self.risks

  def get_products(self) -> List[str]:
    """ Getter / parser for affected products """

    if len(self.affected_products) == 0:
      self.affected_products = self.content["products"]

    return self.affected_products
  
  def get_description(self) -> str:
    """ Getter / parser for description """
    
    if self.description is None:
      self.description = self.content["description"]
      
    return self.description

  def get_cves(self) -> List[str]:
    """ Returns the refs of all the related cves """

    if len(self.cves.keys()) == 0:
      for cve in self.content["cve"]:
        if cve not in self.cves.keys():
          self.cves[cve] = CVE(ref=cve)
        
    return self.cves

  def get_documentations(self, filter: str = None) -> List[str]:
    """ Getter for the documentations """
    
    if len(self.documentations) == 0:
      self.documentations = self.content["documentations"]

    docs = self.documentations

    if filter is not None and filter != "":
      docs = [ d for d in self.documentations if filter not in d ]

    return docs

  def parse(self) -> None:
    """ Parse content section """
    data = {}

    titles = self.content.find_all("h2")

    for t in titles:
      next_el = t.find_next_sibling()

      if next_el.name == "ul":
        data[t.text] = [ li.text for li in next_el.find_all("li") ]
        
      else:
        data[t.text] = next_el.text
        
    data["CVEs"] = set(re.findall(CVE_REGEX, self.content.text))
    data["Documentation"] = re.findall(URL_REGEX, self.content.text)

    self.data = data

  def to_dictionary(self):
    """ Converts current instance into a dictionary """
