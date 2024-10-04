""" Target module handling targeting operations and data gathering """
from typing import List, Dict
from oudjat.utils import ColorPrint
from oudjat.utils import export_csv, import_csv
from oudjat.utils import str_file_option_handle
from oudjat.model.vulnerability import CVE

from . import Base


class Target(Base):
  """ Main enumeration module """

  def __init__(self, options: Dict):
    """ Initialization function """
    super().__init__(options)
    self.results: List[Dict] = []

    str_file_option_handle(self, "TARGET", "FILE")

    # If a csv of cve is provided, populate CVE instances
    if self.options["--cve-list"]:
      print("Importing cve data...")
      
      def cve_import_callback(reader):
        cve_instances = []
        for row in reader:
          cve_instances.append(CVE.create_from_dict(row))

        return cve_instances
      
      cve_import = import_csv(self.options["--cve-list"], cve_import_callback)
      self.options["--cve-list"] = cve_import

  def handle_exception(self, e: Exception, message: str = "") -> None:
    """ Function handling exception for the current class """
    if self.options["--verbose"]:
      print(e)

    if message:
      ColorPrint.red(message)

  def res_2_csv(self) -> None:
    """ Write the results into a CSV file """
    print("\nExporting results to csv...")
    export_csv(self.results, self.options["--export-csv"], '|')

  def run(self) -> None:
    """ Main function called from the cli module """
    # Retreive IP of target and run initial configuration
    self.init()
