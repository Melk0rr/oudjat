""" CVE module addressing common vulnerability behavior """
import re
from enum import Enum

import requests
from bs4 import BeautifulSoup

from oudjat.utils.color_print import ColorPrint

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

  def __init__(self, ref, cvss=0, date="", description=""):
    """ Constructor """
    self.set_ref(ref)
    self.set_cvss(cvss)
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
    if self.check_id(cve_ref):
      self.ref = cve_ref

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

  # ****************************************************************
  # Resolvers

  def check_id(self, cve_ref):
    """ Checks whether the given cve id is valid """
    return re.match(CVE_REGEX, cve_ref)

  def check_cvss(self, cvss_score):
    """ Checks if the provided cvss score is valid """
    return 0 <= cvss_score <= 10

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
    self.description = desc_soup[0].text if len(desc_soup) > 0 else ""

  def parse_publishdate(self, content):
    """ Function to extract cve publish date """
    p_date_soup = content.select("span[data-testid='vuln-published-on']")
    self.publish_date = p_date_soup[0].text if len(p_date_soup) > 0 else ""

  def parse_nist(self):
    """ Function to parse NIST CVE page in order to retreive CVE data """

    # Handle if the target is unreachable
    try:
      req = requests.get(f"{NIST_URL_BASE}{self.get_ref()}")
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
          "link": f"{NIST_URL_BASE}{self.get_ref()}"
      }

      cve_dict.update(more_data)

    return cve_dict
