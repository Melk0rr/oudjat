import re

from typing import List, Dict, Any

from oudjat.connectors.microsoft.ms_api_vars import CVE_REGEX, KB_NUM_REGEX
from oudjat.connectors.microsoft.ms_remed import MSRemed
from oudjat.connectors.microsoft.ms_product import MSProduct

class MSVuln:
  """ Class to manipulate CVE data related to MS products """

  def __init__(self, cve: str):
    """ Constructor """

    if not re.match(CVE_REGEX, cve):
      raise(f"Invalid CVE provided: {cve}")

    self.cve = cve
    self.kbs = {}
    self.products = {}

  def get_cve(self) -> str:
    """ Getter for CVE """
    return self.cve
  
  def get_remediations(self) -> Dict[str, MSRemed]:
    """ Getter for KB list """
    return self.kbs
  
  def get_remediation_numbers(self) -> List[int]:
    """ Returns kb numbers """
    return [ kb_number for kb_number in self.kbs.keys() ]

  def get_impacted_products(self) -> Dict[str, MSProduct]:
    """ Getter for impacted product list """
    return self.products

  def add_kb(self, kb_num: int, kb: MSRemed) -> None:
    """ Adds a KB to vuln KB list """
    if not (re.match(KB_NUM_REGEX, kb_num) or re.match(r'(\w+)$', kb_num)):
      return

    self.kbs[kb_num] = kb

  def to_flat_dict(self) -> List[Dict]:
    """ Converts kbs into dictionaries """
    kb_flat_dicts = []
    for k in self.kbs.values():
      kb_flat_dicts.extend(k.to_flat_dict())

    return [
      { "cve": self.cve, **kb_dict }
      for kb_dict in kb_flat_dicts
    ]

  def to_dict(self) -> Dict[str, Any]:
    """ Converts current vuln into a dict """
    return {
      "cve": self.cve,
      "kbs": [ kb.to_dict() for kb in self.kbs.values() ],
    }