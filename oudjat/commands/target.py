""" Target module handling targeting operations and data gathering """
import csv
import os

from oudjat.utils.color_print import ColorPrint
from oudjat.utils.init_option_handle import str_file_option_handle
from oudjat.watchers.nist_cve import parse_nist_cve

from .base import Base


class Target(Base):
  """ Main enumeration module """
  results = []

  def handle_exception(self, e, message=""):
    """ Function handling exception for the current class """
    if self.options["--verbose"]:
      print(e)
    if message:
      ColorPrint.red(message)


  def max_cve(self, cves):
    """ Returns the cve with the highest cvss score """
    res = { "cve": "", "cvss": None }

    if len(cves) > 0:
      parsed_cves = [ parse_nist_cve(self, cve, mode="min") for cve in cves ]
      res = max(parsed_cves, key=lambda x:x["cvss"])

    return res


  def res_2_csv(self):
    """ Write the results into a CSV file """
    print("\nExporting results to csv...")
    with open(self.options["--export-csv"], "w", encoding="utf-8", newline="") as f:
      writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
      writer.writeheader()
      writer.writerows(self.results)


  def init(self):
    """ Initialization function """
    str_file_option_handle(self, "TARGET", "FILE")


  def run(self):
    """ Main function called from the cli module """
    # Retreive IP of target and run initial configuration
    self.init()
