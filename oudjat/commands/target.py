"""A module to define common target command behavior."""

from collections.abc import Iterator
from multiprocessing import Pool
from typing import Any, override

from oudjat.control.vulnerability import CVE
from oudjat.utils import ColorPrint, FileUtils

from .base import Base


class Target(Base):
    """A class that describes common target command."""

    def __init__(self, options: dict[str, Any]) -> None:
        """
        Create a new instance of Target command.

        Args:
            options (dict[str, Any]): Options passed to the command
        """
        super().__init__(options)
        self.results: list[dict[str, Any]] = []

        self._str_file_option_handle("TARGET", "FILE")

        # If a CSV of CVE is provided, populate CVE instances
        if self.options["--cve-list"]:
            print("Importing cve data...")

            def cve_import_callback(reader: "Iterator"):
                cve_instances = []

                with Pool(processes=5) as pool:
                    for cve in pool.imap_unordered(CVE.create_from_dict, reader):
                        cve_instances.append(cve)

                return cve_instances

            cve_import = FileUtils.import_csv(self.options["--cve-list"], cve_import_callback)
            self.options["--cve-list"] = cve_import

    def _str_file_option_handle(self, string_option: str, file_option: str) -> None:
        """
        Handle the initialization of a list-based option by checking if an existing option is provided as a file path.

        If the `file_option` exists in the `self.options` dictionary, it reads the content of the specified file and splits it into lines,
        filtering out any empty lines to create a list which is then assigned to the `string_option`.

        If the `file_option` does not exist, it assumes that the option is provided as a comma-separated string. It splits this string by commas
        and filters out any empty entries to create a list, which is then assigned to the `string_option`.

        Args:
            string_option (str): The key in the `self.options` dictionary where the resulting list should be stored.
            file_option (str)  : The key in the `self.options` dictionary that, if exists, points to a file path.
        """

        args = (
            FileUtils.import_txt(file_path=self.options[file_option])
            if self.options[file_option]
            else self.options[string_option].split(",")
        )

        self.options[string_option] = list(filter(None, args))

    def handle_exception(self, e: Exception, message: str = "") -> None:
        """
        Handle exception for the current class.

        Args:
            e (Exception): exception tu raise
            message (str): exception message
        """
        if self.options["--verbose"]:
            print(e)

        if message:
            ColorPrint.red(message)

    def res_2_csv(self) -> None:
        """Write the results into a CSV file."""

        print("\nExporting results to csv...")
        FileUtils.export_csv(self.results, self.options["--export-csv"], "|")

    @override
    def run(self) -> None:
        """Run from the cli module."""
