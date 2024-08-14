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

    self.solutions = None
    self.description = None
    self.risks: Set[str] = None
    self.cves: Dict["CVE"] = None
    self.documentations: List[str] = None
    self.affected_products: List[str] = None

  # ****************************************************************
  # Methods

  def get_risks(self, short: bool = True) -> Set["RiskTypes"]:
    """ Getter / parser for the list of risks """
    
    if self.data is not None and self.risks is None:
      risk_set = set()

      for risk in list(RiskTypes):
        if risk.value["fr"].lower() in [ r.lower() for r in self.data.get("Risques", []) ]:
          risk_set.add(risk)

      self.risks = risk_set

    return self.risks

  def get_products(self) -> List[str]:
    """ Getter / parser for affected products """

    if self.data is not None and self.affected_products is None:
      self.affected_products = self.data.get("Systèmes affectés", [])

    return self.affected_products
  
  def get_description(self) -> str:
    """ Getter / parser for description """
    
    if self.data is not None and self.description is None:
      self.description = self.data.get("Résumé", None)
      
    return self.description

  def get_solutions(self) -> str:
    """ Getter / parser for solutions """
    
    if self.data is not None and self.solutions is None:
      self.solutions = self.data.get("Solutions", None)

    return self.solutions

  def get_cves(self) -> List[str]:
    """ Returns the refs of all the related cves """

    if self.data is not None and self.cves is None:
      cves = {}

      for cve in self.data.get("CVEs", []):
        if cve not in cves.keys():
          cves[cve] = CVE(ref=cve)

      self.cves = cves
        
    return self.cves

  def get_documentations(self, filter: str = None) -> List[str]:
    """ Getter for the documentations """
    
    if self.data is not None and self.documentations is None:
      self.documentations = self.data.get("Documentation", [])

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
    content_dict = {}

    if self.data is not None:
      content_dict = {
        "risks": self.get_risks(),
        "products": self.get_products(),
        "description": self.get_description(),
        "cves": self.get_cves(),
        "solutions": self.get_solutions(),
        "documentations": self.get_documentations()
      }

    return content_dict
