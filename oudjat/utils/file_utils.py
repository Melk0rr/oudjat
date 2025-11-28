"""A module that gathers file utilities."""

import csv
import json
import logging
import os
import re
from enum import Enum
from typing import Any, Callable, NamedTuple

import commentjson

from oudjat.utils.context import Context

# TODO: merge txt methods with raw methods

class FileUtils:
    """A class that provides file operations."""

    # ****************************************************************
    # Attributes & Constructors

    logger: "logging.Logger" = logging.getLogger(__name__)

    # ****************************************************************
    # Class methods

    # NOTE: RAW
    @classmethod
    def import_raw(cls, filepath: str, callback: Callable[..., Any] | None = None) -> Any:
        """
        Import the content of a file as a simple raw string.

        Args:
            filepath (str)     : The path to the file.
            callback (Callable): Optional function to run to change final result.

        Returns:
            Any: default is a string, can be any type based on callback changes
        """

        context = Context()

        try:
            full_path = os.path.join(os.getcwd(), filepath)
            cls.logger.info(f"{context}::Importing raw data from {full_path}")

            fd = open(filepath, mode="r")
            file = fd.read()
            fd.close()

            if callback:
                file = callback(file)

            cls.logger.info(f"{context}::Imported raw data from {full_path}")
            cls.logger.debug(f"{context}::{file}")

        except Exception as e:
            raise e

        return file

    @classmethod
    def export_raw(cls, data: str, filepath: str, append: bool = False) -> None:
        """
        Export the content of a file as a simple raw string.

        Args:
            data (str)    : The string to export
            filepath (str): The path where the file will be saved.
            append (bool) : Whether to export in append mode or not
        """

        context = Context()

        full_path = os.path.join(os.getcwd(), filepath)
        cls.logger.info(f"{context}::Exporting raw data in {full_path}")

        try:
            full_path = os.path.join(os.getcwd(), filepath)
            with open(full_path, "a" if append else "w", encoding="utf-8") as file:
                _ = file.write(data)

        except Exception as e:
            raise e

        cls.logger.info(f"{context}::Successfully exported raw data to {filepath}")

    # NOTE: JSON
    @classmethod
    def import_json(cls, filepath: str, callback: Callable[..., Any] | None = None) -> list[Any]:
        """
        Import json data from a specified file.

        Args:
            filepath (str)     : the path to the JSON file.
            callback (Callable): optional function to run to change final result.

        Returns:
            dict or list: The content of the imported JSON file.
        """

        context = Context()

        json_data = None
        try:
            full_path = os.path.join(os.getcwd(), filepath)
            cls.logger.info(f"{context}::Importing JSON data from {full_path}")

            with open(full_path, "r", encoding="utf-8") as json_file:
                json_data = commentjson.load(json_file)

            if callback is not None:
                json_data = callback(json_data)

            cls.logger.info(f"{context}::Successfully imported JSON data from {full_path}")
            cls.logger.debug(f"{context}::{json_data}")

        except Exception as e:
            raise e

        if isinstance(json_data, dict):
            json_data = [json_data]

        return json_data

    @classmethod
    def export_json(cls, data: list[Any], filepath: str) -> None:
        """
        Export data to a JSON file.

        Args:
            data (dict or list): The data to be exported.
            filepath (str)     : The path where the JSON file will be saved.
        """

        context = Context()

        if len(data) == 0:
            print("No data to export !")
            return

        try:
            full_path = os.path.join(os.getcwd(), filepath)
            cls.logger.info(f"{context}::Exporting JSON data to {full_path}")

            with open(full_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            cls.logger.info(f"{context}::Successfully exported JSON data to {full_path}")

        except Exception as e:
            raise e

    # INFO: CSV
    @classmethod
    def import_csv(
        cls, filepath: str, callback: Callable | None = None, delimiter: str | None = None
    ) -> list[Any]:
        """
        Import CSV content into a list of dictionaries.

        Args:
            filepath (str)            : The path to the CSV file.
            callback (callable | None): A callable function to process the data after reading.
            delimiter (str | None)    : The character used as a delimiter in the CSV file.

        Returns:
            list of dicts: The content of the CSV file parsed into a list of dictionaries.
        """

        context = Context()
        cls.logger.info(f"{context}::Importing CSV file {filepath}")

        data: list[Any] = []
        try:
            full_path = os.path.join(os.getcwd(), filepath)
            with open(full_path, "r", encoding="utf-8", newline="") as f:
                # WARN: Try to guess the delimiter if none was specified
                if delimiter is None:
                    first_line = f.readline().strip("\n")
                    _ = f.seek(0)

                    if delimiter is None:
                        delimiter = FileUtils.guess_csv_delimiter(first_line)

                    cls.logger.warning(
                        f"{context}::No delimiter specified, guessed '{delimiter}' as a delimiter"
                    )

                reader = csv.DictReader(f, delimiter=delimiter, skipinitialspace=True)

                raw_data = list(reader)
                if callback is not None:
                    raw_data: list[Any] = callback(raw_data)

                data = raw_data

            cls.logger.info(f"{context}::Successfully imported data from {filepath}")
            cls.logger.debug(f"{context}::{data}")

        except Exception as e:
            raise e

        return data

    @classmethod
    def export_csv(
        cls, data: list[Any], filepath: str, delimiter: str = ",", append: bool = False
    ) -> None:
        """
        Export data into a CSV file.

        Args:
            data (list of dicts)  : The data to be exported.
            filepath (str)        : The path where the CSV file will be saved.
            delimiter (str | None): The character used as a delimiter in the CSV file. Defaults to ",".
            append (bool | None)  : Whether to append to an existing file or overwrite it.
        """

        context = Context()
        cls.logger.info(f"{context}::Exporting CSV data to {filepath}")
        cls.logger.debug(f"{context}::{len(data)} elements to export")

        if len(data) == 0:
            print("No data to export !")
            return

        try:
            full_path = os.path.join(os.getcwd(), filepath)

            mode = "a" if append else "w"
            with open(full_path, mode, encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=delimiter)

                # Write csv headers if not in append mode
                if mode != "a":
                    writer.writeheader()

                writer.writerows(data)

            cls.logger.info(f"{context}Successfully exported CSV data to {filepath}")

        except Exception as e:
            raise e

    # INFO: TXT
    @classmethod
    def import_txt(
        cls,
        filepath: str,
        delete_duplicates: bool = False,
        callback: Callable[..., Any] | None = None,
    ) -> list[Any]:
        """
        Import a text file and optionally remove duplicates.

        Args:
            filepath (str)                 : The path to the text file.
            delete_duplicates (bool | None): Whether to remove duplicate lines from the file.
            callback (callable | None)     : A callable function to process the data after reading.

        Returns:
            list: The content of the text file as a list of strings.
        """

        context = Context()
        cls.logger.info(f"{context}::Importing TXT file {filepath}")

        data = None
        try:
            full_path = os.path.join(os.getcwd(), filepath)
            with open(full_path, encoding="utf-8") as f:
                data = list(filter(None, f.read().split("\n")))

            if delete_duplicates:
                data = list(set(data))

            if callback is not None:
                data = callback(data)

            cls.logger.info(f"{context}::Successfully imported TXT data from {filepath}")
            cls.logger.debug(f"{context}::{data}")

        except Exception as e:
            raise e

        return data

    @classmethod
    def export_txt(cls, data: list[Any], filepath: str, append: bool = False) -> None:
        """
        Export data into a text file.

        Args:
            data (list)         : The data to be exported as strings.
            filepath (str)      : The path where the text file will be saved.
            append (bool | None): Whether to append to an existing file or overwrite it.
        """

        if len(data) == 0:
            print("No data to export !")
            return

        try:
            full_path = os.path.join(os.getcwd(), filepath)

            mode = "a" if append else "w"
            with open(full_path, mode, encoding="utf-8", newline="") as f:
                for line in data:
                    _ = f.write(f"{line}" + "\n")

            cls.logger.info(f"{Context()}::Successfully exported TXT data to {filepath}")

        except Exception as e:
            raise e

    # ****************************************************************
    # Static methods

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
    def guess_csv_delimiter(csv_first_line: str) -> str:
        """
        Guess the CSV delimiter based on the provided first line.

        Helper function that tries to determine the delimiter used in a CSV file.
        It does so by parsing special characters in the header line and returning the character with the highest count

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


class FileTypeProps(NamedTuple):
    """
    A helper class to properly handle FileType properties.

    Args:
        f_import (Callabe): function to import data for a specific file type
        f_export (Callabe): function to export data for a specific file type
    """

    f_import: Callable[..., list[Any]]
    f_export: Callable[..., None]
    mimetype: str


class FileType(Enum):
    """Enumeration of file types to be used by file connector."""

    CSV = FileTypeProps(FileUtils.import_csv, FileUtils.export_csv, mimetype="text/csv")
    JSON = FileTypeProps(FileUtils.import_json, FileUtils.export_json, mimetype="application/json")
    TXT = FileTypeProps(FileUtils.import_txt, FileUtils.export_txt, mimetype="text/plain")
    RAW = FileTypeProps(FileUtils.import_raw, FileUtils.export_raw, mimetype="text/plain")

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
