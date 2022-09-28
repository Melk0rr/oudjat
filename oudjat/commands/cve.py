""" CVE Target class """
import re

from oudjat.utils.color_print import ColorPrint
from oudjat.watchers.nist_cve import parse_nist_cve

from .target import Target

class CVE(Target):
  """ CVE Target """

  unique_cves = set()

  def init(self):
    """ Clean cve target """
    super().init()

    cve_reg = r'CVE-\d{4}-\d{4,7}'

    for i in range(len(self.options["TARGET"])):
      cve = self.options["TARGET"][i]

      if not re.match(cve_reg, cve):
        ColorPrint.red(f"Provided cve {i}: {cve} is not valid")
        self.options["TARGET"].remove(i)

      else:
        ColorPrint.green(f"Gathering data for cve {cve}")
        self.unique_cves.add(cve)


  def run(self):
    """ Run cve target """
    self.init()

    for cve in list(self.unique_cves):
      parse_nist_cve(self, cve)

    if self.options["--export-csv"]:
      super().res_2_csv()
