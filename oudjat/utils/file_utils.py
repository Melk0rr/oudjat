"""A module that gathers file utilities."""

import csv
import json
import os
import re
from enum import Enum
from typing import Any, Callable, NamedTuple

from .color_print import ColorPrint


class FileHandler:
    """A class that provides file operations."""

    @staticmethod
    def check_path(path: str) -> bool:
        """
        Check if the provided path is valid.

        Args:
            path (str): The file path to be checked.

        Raises:
            FileNotFoundError: If the provided path does not point to a valid file.
        """

        return os.path.isfile(path)

    @staticmethod
    def import_raw(file_path: str, callback: Callable[..., Any] | None = None) -> Any:
        """
        Import the content of a file as a simple raw string.

        Args:
            file_path (str)    : The path to the file.
            callback (Callable): Optional function to run to change final result.

        Returns:
            Any: default is a string, can be any type based on callback changes
        """

        fd = open(file_path, mode="r")
        file = fd.read()
        fd.close()

        if callback:
           file = callback(file)

        return file

    # INFO: JSON file functions
    @staticmethod
    def import_json(file_path: str, callback: Callable[..., Any] | None = None) -> list[Any]:
        """
        Import json data from a specified file.

        Args:
            file_path (str)    : the path to the JSON file.
            callback (Callable): optional function to run to change final result.

        Returns:
            dict or list: The content of the imported JSON file.
        """

        json_data = None
        try:
            full_path = os.path.join(os.getcwd(), file_path)
            with open(full_path, "r", encoding="utf-8") as json_file:
                json_data = json.load(json_file)

            if callback is not None:
                json_data = callback(json_data)

            ColorPrint.green(f"Successfully imported JSON data from {full_path}")

        except Exception as e:
            raise e

        if isinstance(json_data, dict):
            json_data = [json_data]

        return json_data

    @staticmethod
    def export_json(data: list[Any], file_path: str) -> None:
        """
        Export data to a JSON file.

        Args:
            data (dict or list): The data to be exported.
            file_path (str)    : The path where the JSON file will be saved.
        """

        if len(data) == 0:
            print("No data to export !")
            return

        try:
            full_path = os.path.join(os.getcwd(), file_path)

            with open(full_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            ColorPrint.green(f"Successfully exported JSON data to {full_path}")

        except Exception as e:
            raise e

    # INFO: CSV file functions
    @staticmethod
    def guess_csv_delimiter(csv_first_line: str) -> str:
        """
        Guess the CSV delimiter based on the provided first line.

        Helper function that tries to determine the delimiter used in a CSV file. It does so by parsing special characters in the header line and returning the character with the highest count

        Args:
            csv_first_line (str): the CSV header line (in theory). The user can provide any other line if he whishes

        Returns:
            str: the delimiter used (?) in the CSV file based on the provided line. Or ',' if no delimiter are found
        """
        delimiter = ","
        delimiter_list: list[str] = re.findall(r"\W", csv_first_line)

        if len(delimiter_list) > 0:
            delimiter_counts: dict[str, int] = {}
            for c in delimiter_list:
                if c not in delimiter_counts:
                    delimiter_counts[c] = 1

                delimiter_counts[c] += 1

            delimiter: str = max(delimiter_counts, key=lambda d: delimiter_counts[d])

        return delimiter

    @staticmethod
    def import_csv(
        file_path: str, callback: Callable | None = None, delimiter: str | None = None
    ) -> list[Any]:
        """
        Import CSV content into a list of dictionaries.

        Args:
            file_path (str)              : The path to the CSV file.
            callback (callable, optional): A callable function to process the data after reading.
            delimiter (str, optional)    : The character used as a delimiter in the CSV file.

        Returns:
            list of dicts: The content of the CSV file parsed into a list of dictionaries.
        """

        data: list[Any] = []
        try:
            full_path = os.path.join(os.getcwd(), file_path)
            with open(full_path, "r", encoding="utf-8", newline="") as f:
                # WARN: Try to guess the delimiter if none was specified
                if delimiter is None:
                    first_line = f.readline().strip("\n")
                    _ = f.seek(0)

                    if delimiter is None:
                        delimiter = FileHandler.guess_csv_delimiter(first_line)

                    print(f"\nNo delimiter specified, guessed '{delimiter}' as a delimiter")

                reader = csv.DictReader(f, delimiter=delimiter, skipinitialspace=True)

                raw_data = list(reader)
                if callback is not None:
                    raw_data: list[Any] = callback(raw_data)

                data = raw_data

            ColorPrint.green(f"Successfully imported CSV data from {file_path}")

        except Exception as e:
            raise e

        return data

    @staticmethod
    def export_csv(
        data: list[Any], file_path: str, delimiter: str = ",", append: bool = False
    ) -> None:
        """
        Export data into a CSV file.

        Args:
            data (list of dicts)     : The data to be exported.
            file_path (str)          : The path where the CSV file will be saved.
            delimiter (str, optional): The character used as a delimiter in the CSV file. Defaults to ",".
            append (bool, optional)  : Whether to append to an existing file or overwrite it.
        """

        if len(data) == 0:
            print("No data to export !")
            return

        try:
            full_path = os.path.join(os.getcwd(), file_path)

            mode = "a" if append else "w"
            with open(full_path, mode, encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=delimiter)

                # Write csv headers if not in append mode
                if mode != "a":
                    writer.writeheader()

                writer.writerows(data)

            ColorPrint.green(f"Successfully exported CSV data to {file_path}")

        except Exception as e:
            raise e

    # INFO: TXT file functions
    @staticmethod
    def import_txt(
        file_path: str, delete_duplicates: bool = False, callback: Callable[..., Any] | None = None
    ) -> list[Any]:
        """
        Import a text file and optionally remove duplicates.

        Args:
            file_path (str)                   : The path to the text file.
            delete_duplicates (bool, optional): Whether to remove duplicate lines from the file.
            callback (callable, optional)     : A callable function to process the data after reading.

        Returns:
            list: The content of the text file as a list of strings.
        """

        data = None

        try:
            full_path = os.path.join(os.getcwd(), file_path)
            with open(full_path, encoding="utf-8") as f:
                data = list(filter(None, f.read().split("\n")))

            if delete_duplicates:
                data = list(set(data))

            if callback is not None:
                data = callback(data)

            ColorPrint.green(f"Successfully imported TXT data from {file_path}")

        except Exception as e:
            raise e

        return data

    @staticmethod
    def export_txt(data: list[Any], file_path: str, append: bool = False) -> None:
        """
        Export data into a text file.

        Args:
            data (list)             : The data to be exported as strings.
            file_path (str)         : The path where the text file will be saved.
            append (bool, optional) : Whether to append to an existing file or overwrite it.
        """

        if len(data) == 0:
            print("No data to export !")
            return

        try:
            full_path = os.path.join(os.getcwd(), file_path)

            mode = "a" if append else "w"
            with open(full_path, mode, encoding="utf-8", newline="") as f:
                for line in data:
                    _ = f.write(f"{line}" + "\n")

            ColorPrint.green(f"Successfully exported TXT data to {file_path}")

        except Exception as e:
            raise e


class FileTypeProps(NamedTuple):
    """
    A helper class to properly handle FileType properties.

    Args:
        f_import (Callabe): function to import data for a specific file type
        f_export (Callabe): function to export data for a specific file type
    """

    f_import: Callable[..., list[Any]]
    f_export: Callable[..., None]


class FileType(Enum):
    """Enumeration of file types to be used by file connector."""

    CSV = FileTypeProps(FileHandler.import_csv, FileHandler.export_csv)
    JSON = FileTypeProps(FileHandler.import_json, FileHandler.export_json)
    TXT = FileTypeProps(FileHandler.import_txt, FileHandler.export_txt)

    @property
    def f_import(self) -> Callable[..., list[Any]]:
        """
        Get the import function for the file type.

        Returns:
            Callable: The import function as a callable object.
        """

        return self._value_.f_import

    @property
    def f_export(self) -> Callable[..., None]:
        """
        Get the export function for the file type.

        Returns:
            Callable: The export function as a callable object.
        """

        return self._value_.f_export
