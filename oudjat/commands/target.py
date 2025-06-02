from multiprocessing import Pool
from typing import Dict, List

from oudjat.control.vulnerability import CVE
from oudjat.utils import ColorPrint, FileHandler

from .base import Base


class Target(Base):
    """Main enumeration module"""

    def __init__(self, options: Dict):
        """Initialization function"""
        super().__init__(options)
        self.results: List[Dict] = []

        self.str_file_option_handle("TARGET", "FILE")

        # If a CSV of CVE is provided, populate CVE instances
        if self.options["--cve-list"]:
            print("Importing cve data...")

            def cve_import_callback(reader):
                cve_instances = []

                with Pool(processes=5) as pool:
                    for cve in pool.imap_unordered(CVE.create_from_dict, reader):
                        cve_instances.append(cve)

                return cve_instances

            cve_import = FileHandler.import_csv(self.options["--cve-list"], cve_import_callback)
            self.options["--cve-list"] = cve_import

    def str_file_option_handle(self, string_option: str, file_option: str) -> None:
        """
        This function handles the initialization of a list-based option by checking if an existing option is provided as a file path.
        If the `file_option` exists in the `self.options` dictionary, it reads the content of the specified file and splits it into lines,
        filtering out any empty lines to create a list which is then assigned to the `string_option`.

        If the `file_option` does not exist, it assumes that the option is provided as a comma-separated string. It splits this string by commas
        and filters out any empty entries to create a list, which is then assigned to the `string_option`.

        Args:
            self (object)      : The instance of the class containing the options dictionary.
            string_option (str): The key in the `self.options` dictionary where the resulting list should be stored.
            file_option (str)  : The key in the `self.options` dictionary that, if exists, points to a file path.
        """

        args = (
            FileHandler.import_txt(file_path=self.options[file_option])
            if self.options[file_option]
            else self.options[string_option].split(",")
        )

        self.options[string_option] = list(filter(None, args))

    def handle_exception(self, e: Exception, message: str = "") -> None:
        """Function handling exception for the current class"""
        if self.options["--verbose"]:
            print(e)

        if message:
            ColorPrint.red(message)

    def res_2_csv(self) -> None:
        """Write the results into a CSV file"""

        print("\nExporting results to csv...")
        FileHandler.export_csv(self.results, self.options["--export-csv"], "|")

    def run(self) -> None:
        """Main function called from the cli module"""

        # Retreive IP of target and run initial configuration
        self.init()
