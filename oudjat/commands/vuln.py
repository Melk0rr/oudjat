""" CVE Target class """
from oudjat.utils.color_print import ColorPrint
from oudjat.watchers.cve import CVE

from .target import Target


class Vuln(Target):
  """ CVE Target """

  unique_cves = set()

  def __init__(self, options):
    """ Constructor """
    super().__init__(options)

    target_cves = set(self.options["TARGET"])

    print(f"{len(target_cves)} CVEs to investigate...\n")

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
      self.results.append(cve.to_dictionary(minimal=False))

    if self.options["--export-csv"]:
      super().res_2_csv()
      