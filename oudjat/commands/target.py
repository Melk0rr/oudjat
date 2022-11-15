""" Target module handling targeting operations and data gathering """
import csv
import os

from oudjat.utils.color_print import ColorPrint
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
    parsed_cves = [ parse_nist_cve(self, cve) for cve in cves ]
    return max(parsed_cves, key=lambda x:x["cvss"])


  def res_2_csv(self):
    """ Write the results into a CSV file """
    print("\nExporting results to csv...")
    with open(self.options["--export-csv"], "w", encoding="utf-8", newline="") as f:
      writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
      writer.writeheader()
      writer.writerows(self.results)


  def init(self):
    """ Initialization function """
    # If user set file option: define target with file content
    if self.options["FILE"]:
      full_path = os.path.join(os.getcwd(), self.options["FILE"])

      with open(full_path, encoding="utf-8") as f:
        self.options["TARGET"] = list(filter(None, f.read().split('\n')))

    # Else: the target is defined by the target option
    else: self.options["TARGET"] = list(filter(None, self.options["TARGET"].split(",")))


  def run(self):
    """ Main function called from the cli module """
    # Retreive IP of target and run initial configuration
    self.init()
