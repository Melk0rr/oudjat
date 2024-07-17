""" CVE module addressing common vulnerability behavior """
import re
import datetime
import requests

from enum import Enum
from typing import List, Dict, Union
from bs4 import BeautifulSoup

from oudjat.utils.file import import_csv
from oudjat.utils.color_print import ColorPrint
from oudjat.connectors.nist.nist_connector import NistConnector

CVE_REGEX = r'CVE-\d{4}-\d{4,7}'
NIST_URL_BASE = "https://nvd.nist.gov/vuln/detail/"


class Severity(Enum):
  """ Severity enumeration """
  NONE = {"min": 0, "max": 0}
  LOW = {"min": 0.1, "max": 3.9}
  MEDIUM = {"min": 4.0, "max": 6.9}
  HIGH = {"min": 7.0, "max": 8.9}
  CRITICAL = {"min": 9.0, "max": 10.0}


class CVE:
  """ CVE class """

  # ****************************************************************
  # Attributes & Constructors

  NIST_ATTR = ["published", "lastModified", "vulnStatus", "descriptions", "metrics", "references"]

  def __init__(
    self,
    ref: str,
    cvss: float = 0,
    date: Union[str, datetime.datetime] = None,
    description: str = None
  ):
    """ Constructor """
    if not self.check_ref(ref):
      raise ValueError(f"{ref} is not a valid CVE id")

    self.ref = ref
    
    self.cvss = 0
    self.set_cvss(float(cvss))
    self.severity = Severity.NONE

    self.link = f"{NIST_URL_BASE}{self.ref}"

    self.status = None
    self.publish_date = date
    self.description = description
    self.references = []

  # ****************************************************************
  # Getters and Setters

  def get_ref(self) -> str:
    """ Getter for the CVE reference """
    return self.ref

  def get_cvss(self) -> float:
    """ Getter for the CVSS score """
    return self.cvss

  def get_severity(self) -> str:
    """ Getter for the severity """
    return self.severity.name
  
  def get_link(self) -> str:
    """ Getter for current CVE link """
    return self.link

  def set_cvss(self, cvss_score: float) -> None:
    """ Setter for the vulnerability CVSS score """
    if self.check_cvss(cvss_score):
      self.cvss = cvss_score
      self.resolve_severity()

    else:
      ColorPrint.red(
          f"{cvss_score} is not a valid CVSS score. You must provide a value between 0 and 10")

  def set_from_dict(self, cve_dict: Dict) -> None:
    """ Set CVE informations from dictionary """
    self.cvss = cve_dict.get("cvss")
    self.publish_date = cve_dict.get("publish_date", "")
    self.description = cve_dict.get("description", "")

  def copy(self, cve: "CVE") -> None:
    """ Copy the given cve informations """
    self.set_from_dict(cve.to_dictionary(minimal=False))
    print(self.to_string())

  # ****************************************************************
  # Resolvers

  def resolve_severity(self) -> None:
    """ Resolves the severity based on the CVSS score """
    for severity in list(Severity):
      if severity.value["min"] <= self.cvss <= severity.value["max"]:
        self.severity = severity

  # ****************************************************************
  # Parsers

  def parse_nist(self, verbose: bool = True) -> None:
    """ Function to parse NIST CVE page in order to retreive CVE data """
    nist = NistConnector()
    nist_data = nist.search(search_filter=self.ref, attributes=self.NIST_ATTR)
    
    self.status = nist_data["vulnStatus"]
    self.publish_date = nist_data["published"]
    self.description = nist_data["description"][0]["value"]
    
    metrics = nist_data["metrics"]
    metric_data = metric[metric.keys()[0]]
    cvss_data = metric_data["cvssData"]
    
    self.set_cvss(cvss_data["baseScore"])

    self.references = [ r["url"] for r in nist_data["references"] ]

    if verbose:
      print(self.to_string())

  # ****************************************************************
  # Converters

  def to_string(self, showSeverity: bool = False) -> str:
    """ Converts the current instance to a string """
    base = f"{self.ref}: {self.cvss}"

    if showSeverity:
      base += f"({self.severity.name})"

    return base

  def to_dictionary(self, minimal: bool = True) -> Dict:
    """ Converts the current instance to a dictionary """
    return {
      "cve": self.ref,
      "cvss": self.cvss,
      "published": self.publish_date,
      "status": self.status,
      "description": self.description,
      "link": self.link,
      "references": self.references
    }
  
  # ****************************************************************
  # Static methods

  @staticmethod
  def check_ref(cve_ref: str) -> bool:
    """ Checks whether the given cve id is valid """
    return re.match(CVE_REGEX, cve_ref)
  
  @staticmethod
  def check_cvss(cvss_score: float) -> bool:
    """ Checks whether the given cvss score is valid """
    return 0 <= cvss_score <= 10
  
  @staticmethod
  def create_from_dict(cve_dict: Dict) -> "CVE":
    """ Creates a CVE instance from a dictionary """
    return CVE(
      cve_dict.get("ref"),
      cve_dict.get("cvss"),
      cve_dict.get("publish_date", ""),
      cve_dict.get("description", "")
    )
    
  @staticmethod
  def find_cve_by_ref(ref, cve_list: List["CVE"]) -> "CVE":
    """ Find a CVE instance by ref in a list of CVEs """
    if not CVE.check_ref(ref):
      raise ValueError(f"Invalid CVE reference provided: {ref}")
    
    res = None

    for cve in cve_list:
      if cve.get_ref() == ref:
        res = cve
    
    return res
