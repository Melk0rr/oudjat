# TODO: rewrite TenableSCConnector and implement it
from typing import Dict

# from oudjat.connectors.tenable.sc.tenablesc_connector import TenabeSCConnector

from .target import Target

class SC(Target):
  """ Tenable SC module class """

  sc_commands = {
  }

  def __init__(self, options: Dict):
    """ Constructor """
    super().__init__(options)

    self.my_sc = None

    # try:
    #   from oudjat.API import TSC_ACCESS_KEY, TSC_SECRET_KEY
    #   self.my_sc = TenabeSCConnector('scanvuln.ramsaysante.fr', TSC_ACCESS_KEY, TSC_SECRET_KEY)

    #   print(self.my_sc.vulns)

    # except ValueError:
    #   raise ValueError("Unable to import SC API keys")

  def sc_process(self) -> None:
    """ Tenable.sc default process """


  def run(self) -> None:
    """ Run sc process on targets """

    # with Pool(processes=5) as pool:
    #   for cve_dict in pool.imap_unordered(self.sc_process, self.unique_cves):
    #     self.results.append(cve_dict)
    self.sc_process()

    if self.options["--export-csv"]:
      super().res_2_csv()