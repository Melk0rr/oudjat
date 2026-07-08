"""A module that gathers file utilities."""

import csv
import logging
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import Any, Callable, NamedTuple

import orjson
import polars as pl

from oudjat.utils.context import Context
from oudjat.utils.types import DataType


class FileImportError(Exception):
    """
    A helper class to handle file import errors.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of FileImportError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)


class FileExportError(Exception):
    """
    A helper class to handle file export errors.
    """

    def __init__(self, message: str) -> None:
        """
        Create a new instance of FileExportError.

        Args:
            message (str): Error message
        """

        self.message: str = message
        super().__init__(self.message)


class FileUtils:
    """A class that provides file operations."""

    # ****************************************************************
    # Attributes & Constructors

    logger: "logging.Logger" = logging.getLogger(__name__)

    # ****************************************************************
    # Helper functions

    @classmethod
    def _check_path(cls, filepath: "str | Path") -> "Path":
        """
        Unify a file path into a Path instance.

        Takes an input file path wich is either a string or a Path instance.
        And return only a Path instance.

        Args:
            filepath (str | Path): The file path to unify

        Returns:
            Path: The Path instance
        """

        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Provided path {filepath} does not exist")

        return filepath

    # ****************************************************************
    # Class methods

    # NOTE: JSON
    @classmethod
    def import_json(
        cls, filepath: "str | Path", callback: Callable[..., Any] | None = None
    ) -> list[Any]:
        """
        Import json data from a specified file.

        Args:
            filepath (str | Path): the path to the JSON file.
            callback (Callable)  : optional function to run to change final result.

        Returns:
            dict or list: The content of the imported JSON file.
        """

        filepath = cls._check_path(filepath)
        json_data = None

        try:
            full_path = filepath.absolute()
            cls.logger.info(f"Importing JSON data from {full_path}")

            json_data = orjson.loads(filepath.read_bytes())

            if callback is not None:
                json_data = callback(json_data)

            cls.logger.info(f"Successfully imported JSON data from {full_path}")
            cls.logger.debug(f"{json_data}")

        except FileImportError as e:
            raise FileImportError(f"{e}")

        if isinstance(json_data, dict):
            json_data = [json_data]

        return json_data

    @classmethod
    def export_json(
        cls, data: list[dict[str, Any]] | dict[str, Any], filepath: "str | Path"
    ) -> None:
        """
        Export data to a JSON file.

        Args:
            data (dict or list): The data to be exported.
            filepath (str)     : The path where the JSON file will be saved.
        """

        context = Context()

        if len(data) == 0:
            cls.logger.error(f"{context}::No data to export as JSON!")
            return

        filepath = Path(filepath)
        full_path = filepath.absolute()

        try:
            cls.logger.info(f"Exporting JSON data to {full_path}")

            _ = filepath.write_bytes(orjson.dumps(data, option=orjson.OPT_INDENT_2))

            cls.logger.info(f"Successfully exported JSON data to {full_path}")

        except FileExportError as e:
            raise FileExportError(f"{context}::{e}")

    # INFO: CSV
    @classmethod
    def import_csv(
        cls, filepath: "str | Path", callback: Callable | None = None, delimiter: str | None = None
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

        cls.logger.info(f"Importing CSV file {filepath}")

        filepath = cls._check_path(filepath)
        csv_data: list[Any] = []

        try:
            # WARN: Try to guess the delimiter if none was specified
            if delimiter is None:
                delimiter = FileUtils.guess_csv_delimiter(filepath)

                cls.logger.warning(f"No delimiter specified, guessed '{delimiter}' as a delimiter")

                csv_data = pl.read_csv(filepath.absolute(), separator=delimiter)

                if callback is not None:
                    csv_data = callback(csv_data)

            cls.logger.info(f"Successfully imported data from {filepath}")
            cls.logger.debug(f"{csv_data}")

        except FileImportError as e:
            raise FileImportError(f"{e}")

        return csv_data

    @classmethod
    def export_csv(
        cls,
        data: list[Any],
        filepath: "str | Path",
        delimiter: str = ",",
        include_header: bool = True,
    ) -> None:
        """
        Export data into a CSV file.

        By default, the headers are extracted from the first element keys.
        You can specify a list of fieldnames to set the CSV headers.

        Args:
            data (list of dicts)  : The data to be exported.
            filepath (str)        : The path where the CSV file will be saved.
            delimiter (str | None): The character used as a delimiter in the CSV file. Defaults to ",".
            include_header (boo)  : Wheither to include the csv headers or not
        """

        context = Context()

        filepath = Path(filepath)

        cls.logger.info(f"Exporting CSV data to {filepath}")
        cls.logger.debug(f"{len(data)} elements to export")

        if len(data) == 0:
            cls.logger.error(f"{context}::No data to export as CSV!")
            return

        try:
            full_path = filepath.absolute()

            df = pl.DataFrame(data)
            df.write_csv(full_path, separator=delimiter, include_header=include_header)

            cls.logger.info(f"Successfully exported CSV data to {filepath}")

        except FileExportError as e:
            raise FileExportError(f"{context}::{e}")

    # INFO: TXT
    @classmethod
    def import_txt(
        cls,
        filepath: "str | Path",
        raw: bool = False,
        delete_duplicates: bool = False,
        callback: Callable[..., Any] | None = None,
    ) -> list[Any]:
        """
        Import a text file and optionally remove duplicates.

        Args:
            filepath (str)                 : The path to the text file.
            raw (bool)                     : Whether to import the txt file as a raw string
            delete_duplicates (bool | None): Whether to remove duplicate lines from the file.
            callback (callable | None)     : A callable function to process the data after reading.

        Returns:
            list: The content of the text file as a list of strings.
        """

        cls.logger.info(f"Importing TXT file {filepath}")

        filepath = cls._check_path(filepath)
        data = None

        try:
            full_path = filepath.absolute()

            data = full_path.read_text()

            if not raw:
                data = list(filter(None, data.split("\n")))

                if delete_duplicates:
                    data = list(set(data))

            if callback is not None:
                data = callback(data)

            cls.logger.info(f"Successfully imported TXT data from {filepath}")
            cls.logger.debug(f"{Context()}::Imported > {data}")

        except FileImportError as e:
            raise FileImportError(f"{e}")

        return data if isinstance(data, list) else [data]

    @classmethod
    def export_txt(cls, data: Any, filepath: "str | Path", raw: bool = False) -> None:
        """
        Export data into a text file.

        Args:
            data (list)         : The data to be exported as strings
            filepath (str)      : The path where the text file will be saved
            raw (bool)          : Whether to export the data as a raw string
        """

        context = Context()

        if len(data) == 0:
            cls.logger.error(f"{context}::No data to export !")
            return

        filepath = Path(filepath)
        full_path = filepath.absolute()

        try:
            if raw:
                _ = full_path.write_text(data)

            else:
                lines = "\n".join(data)
                _ = full_path.write_text(lines)

            cls.logger.info(f"Successfully exported{raw and ' raw'} TXT data to {filepath}")

        except FileExportError as e:
            raise FileExportError(f"{e}")

    # ****************************************************************
    # Static methods

    @staticmethod
    def parse_csv_str(csv_str: str, delimiter: str | None = None) -> "DataType":
        """
        Convert a CSV string into a list of dictionaries.

        Args:
            csv_str (str)         : CSV string to convert
            delimiter (str | None): The delimiter to use to parse the CSV string

        Returns:
            DataType: Parsed CSV string as a list of dictionaries
        """

        f = StringIO(csv_str)

        if delimiter is None:
            first_line = f.readline().strip("\n")
            _ = f.seek(0)

            delimiter = FileUtils.guess_csv_delimiter(first_line)

        return list(csv.DictReader(f, delimiter=delimiter, skipinitialspace=True))

    @staticmethod
    def guess_csv_delimiter(filepath: "str | Path", sample_size: int = 2048) -> str:
        """
        Guess the CSV delimiter based on a sample of the target file.

        Helper function that tries to determine the delimiter used in a CSV file.
        It does so by parsing special characters in the header line and returning the character with the highest count

        Args:
            filepath (str | Path): The CSV header line (in theory). The user can provide any other line if he whishes
            sample_size (int)    : The size of the sample that will be used to guess the delimiter

        Returns:
            str: the delimiter used (?) in the CSV file based on the provided line. Or ',' if no delimiter are found
        """

        delimiter = ","

        if not isinstance(filepath, Path):
            filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Provided path {filepath} does not exist")

        with filepath.open("r", encoding="utf-8") as f:
            sample = f.read(sample_size)

            sniffer = csv.Sniffer()
            sniffed_sample = sniffer.sniff(sample)

            delimiter = sniffed_sample.delimiter

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
