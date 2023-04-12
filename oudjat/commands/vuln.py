""" CVE Target class """
import re

from oudjat.utils.color_print import ColorPrint
from oudjat.watchers.cve import CVE

from .target import Target


class Vuln(Target):
  """ CVE Target """

  unique_cves = set()

  def __init__(self):
    """ Constructor """
    super().__init__()

    target_cves = set(self.options["TARGET"])

    for ref in target_cves:
      try:
        cve = CVE(ref)
        self.unique_cves.add(cve)

      except ValueError:
        ColorPrint.red(f"Invalid CVE reference provided {ref}")

  def run(self):
    """ Run cve target """

    for cve in self.unique_cves:
      cve.parse_nist()
      self.results.append(cve.to_dictionary())

    if self.options["--export-csv"]:
      super().res_2_csv()
