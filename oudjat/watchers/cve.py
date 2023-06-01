""" CVE module addressing common vulnerability behavior """
import re
from enum import Enum

import requests
from bs4 import BeautifulSoup

from oudjat.utils.color_print import ColorPrint
from oudjat.utils.file import import_csv

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

  ref = ""
  cvss = 0
  severity = Severity.NONE
  publish_date = ""
  description = ""
  link = ""

  def __init__(self, ref, cvss=0, date="", description=""):
    """ Constructor """
    self.set_ref(ref)
    self.set_cvss(float(cvss))
    self.publish_date = date
    self.description = description

  # ****************************************************************
  # Getters and Setters

  def get_ref(self):
    """ Getter for the CVE reference """
    return self.ref

  def get_cvss(self):
    """ Getter for the CVSS score """
    return self.cvss

  def get_severity(self):
    """ Getter for the severity """
    return self.severity.name

  def set_ref(self, cve_ref):
    """ Setter for the CVE id """
    if self.check_ref(cve_ref):
      self.ref = cve_ref
      self.link = f"{NIST_URL_BASE}{self.ref}"

    else:
      raise ValueError(f"{cve_ref} is not a valid CVE id")

  def set_cvss(self, cvss_score):
    """ Setter for the vulnerability CVSS score """
    if self.check_cvss(cvss_score):
      self.cvss = cvss_score
      self.resolve_severity()

    else:
      ColorPrint.red(
          f"{cvss_score} is not a valid CVSS score. You must provide a value between 0 and 10")

  def set_from_dict(self, cve_dict):
    """ Set CVE informations from dictionary """
    self.cvss = cve_dict.get("cvss")
    self.publish_date = cve_dict.get("publish_date", "")
    self.description = cve_dict.get("description", "")

  def copy(self, cve):
    """ Copy the given cve informations """
    self.set_from_dict(cve.to_dictionary(minimal=False))
    print(self.to_string())

  # ****************************************************************
  # Resolvers

  def resolve_severity(self):
    """ Resolves the severity based on the CVSS score """
    for severity in list(Severity):
      if severity.value["min"] <= self.cvss <= severity.value["max"]:
        self.severity = severity

  # ****************************************************************
  # Parsers

  def parse_cvss(self, content):
    """ Function to extract CVSS score """
    cvss_match = re.findall(
        r'(?:[1-9].[0-9]) (?:LOW|MEDIUM|HIGH|CRITICAL)', content.text)

    if len(cvss_match) > 0:
      self.set_cvss(float(cvss_match[0].split(" ")[0]))

    else:
      print(f"Could not find CVSS score for {self.ref}")

  def parse_description(self, content):
    """ Function to extract description """
    desc_soup = content.select("p[data-testid='vuln-description']")
    self.description = desc_soup[0].text.replace("\n", " ") if len(desc_soup) > 0 else ""

  def parse_publishdate(self, content):
    """ Function to extract cve publish date """
    p_date_soup = content.select("span[data-testid='vuln-published-on']")
    self.publish_date = p_date_soup[0].text if len(p_date_soup) > 0 else ""

  def parse_nist(self):
    """ Function to parse NIST CVE page in order to retreive CVE data """

    # Handle if the target is unreachable
    try:
      req = requests.get(self.link)
      soup = BeautifulSoup(req.content, 'html.parser')

    except ConnectionError as e:
      ColorPrint.red(
          f"Error while requesting {self.get_ref()}. Make sure the target is accessible")

    # Minimal information retreived is the CVSS score
    self.parse_cvss(soup)
    self.parse_description(soup)
    self.parse_publishdate(soup)

    print(self.to_string())

  # ****************************************************************
  # Converters

  def to_string(self, showSeverity=False):
    """ Converts the current instance to a string """
    base = f"{self.ref}: {self.cvss}"

    if showSeverity:
      base += f"({self.severity.name})"

    return base

  def to_dictionary(self, minimal=True):
    """ Converts the current instance to a dictionary """
    cve_dict = {"ref": self.ref, "cvss": self.cvss}

    # If user specifies it : provide more data in the dictionary
    if not minimal:
      more_data = {
          "severity": self.severity,
          "publish_date": self.publish_date,
          "description": self.description,
          "link": self.link
      }

      cve_dict.update(more_data)

    return cve_dict
  
  # ****************************************************************
  # Static methods

  @staticmethod
  def check_ref(cve_ref):
    """ Checks whether the given cve id is valid """
    return re.match(CVE_REGEX, cve_ref)
  
  @staticmethod
  def check_cvss(cvss_score):
    """ Checks whether the given cvss score is valid """
    return 0 <= cvss_score <= 10
  
  @staticmethod
  def create_from_dict(cve_dict):
    """ Creates a CVE instance from a dictionary """
    cve = CVE(cve_dict.get("ref"), cve_dict.get("cvss"), cve_dict.get("publish_date", ""), cve_dict.get("description", ""))
    
    return cve
    

  @staticmethod
  def find_cve_by_ref(ref, cve_list):
    """ Find a CVE instance by ref in a list of CVEs """
    if not CVE.check_ref(ref):
      raise ValueError(f"Invalid CVE reference provided: {ref}")
    
    res = None

    for cve in cve_list:
      if cve.get_ref() == ref:
        res = cve
    
    return res
