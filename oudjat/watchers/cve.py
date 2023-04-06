""" CVE module addressing common vulnerability behavior """
import re
from datetime import datetime
from enum import Enum

from oudjat.utils.color_print import ColorPrint


class Severity(Enum):
  """ Severity enumeration """
  NONE = {"min": 0, "max": 0}
  LOW = {"min": 0.1, "max": 3.9}
  MEDIUM = {"min": 4.0, "max": 6.9}
  HIGH = {"min": 7.0, "max": 8.9}
  CRITICAL = {"min": 9.0, "max": 10.0}


class CVE:
  """ CVE class """

  ref = ""
  cvss = 0
  severity = Severity.NONE
  publish_date = ""
  description = ""
  regex = r'CVE-\d{4}-\d{4,7}'

  def __init__(self, ref, cvss = 0, date = "", description = ""):
    """ Constructor """
    self.set_ref(ref)
    self.set_cvss(cvss)
    self.set_publish_date(date)
    self.description = description

  def get_ref(self):
    """ Getter for the CVE reference """
    return self.ref

  def get_cvss(self):
    """ Getter for the CVSS score """
    return self.cvss

  def get_severity(self):
    """ Getter for the severity """
    return self.severity.name

  def set_publish_date(self, date):
    """ Setter for publish date """
    try:
      self.publish_date = datetime.strptime(date)

    except:
      ColorPrint.red(f"Invalid publish date provided")

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

    else:
      ColorPrint.red(f"{cvss_score} is not a valid CVSS score. You must provide a value between 0 and 10")

  def check_id(self, cve_ref):
    """ Checks whether the given cve id is valid """
    return re.match(self.regex, cve_ref)

  def check_cvss(self, cvss_score):
    """ Checks if the provided cvss score is valid """
    return 0 <= cvss_score <= 10

  def resolve_severity(self):
    """ Resolves the severity based on the CVSS score """
    for severity in list(Severity):
      if severity.value["min"] <= self.cvss <= severity.value["max"]:
        self.severity = severity

  def to_string(self, showSeverity=False):
    """ Returns a string based on the CVE ref and CVSS score """
    base = f"{self.ref}: {self.cvss}"

    if showSeverity:
      base += f"({self.severity.name})"

    return base

  

cve = CVE("CVE-2022-2880", 7.5)
cve.resolve_severity()

print(cve.to_string(showSeverity=True))