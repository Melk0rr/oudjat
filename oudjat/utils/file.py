import csv
import json
import os
import re
from enum import Enum
from typing import Any, Callable, Dict, List, Union

from .color_print import ColorPrint


class FileHandler:
    @staticmethod
    def check_path(path: str) -> None:
        """
        Check if the provided path is valid.

        Args:
            path (str): The file path to be checked.

        Raises:
            FileNotFoundError: If the provided path does not point to a valid file.
        """

        if not os.path.isfile(path):
            raise (f"Invalid file path provided: {path}")

    # INFO: JSON file functions
    @staticmethod
    def import_json(file_path: str, callback: Callable = None) -> Union[Dict, List]:
        """
        Helper function to import json data from a specified file.

        Args:
            file_path (str): The path to the JSON file.

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

            ColorPrint.green(f"Successfully imported JSON data from {file_path}")

        except Exception as e:
            raise e

        return json_data

    @staticmethod
    def export_json(data: Union[List[Dict], Dict], file_path: str) -> None:
        """
        Exports data to a JSON file.

        Args:
            data (dict or list): The data to be exported.
            file_path (str)    : The path where the JSON file will be saved.
        """

        if len(data) == 0:
            print("No data to export !")
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            ColorPrint.green(f"Successfully exported JSON data to {file_path}")

        except Exception as e:
            raise e

    # INFO: CSV file functions
    @staticmethod
    def import_csv(file_path: str, callback: Callable = None, delimiter: str = None) -> List[Dict]:
        """
        Helper function to import CSV content into a list of dictionaries.

        Args:
            file_path (str)              : The path to the CSV file.
            callback (callable, optional): A callable function to process the data after reading.
            delimiter (str, optional)    : The character used as a delimiter in the CSV file.

        Returns:
            list of dicts: The content of the CSV file parsed into a list of dictionaries.
        """

        full_path = os.path.join(os.getcwd(), file_path)
        data = None

        try:
            with open(full_path, "r", encoding="utf-8", newline="") as f:
                # WARN: Try to guess the delimiter if none was specified
                if not delimiter:
                    first_line = f.readline().strip("\n")
                    f.seek(0)
                    delimiter = re.findall(r"\W", first_line)[0]

                    print(f"\nNo delimiter specified, guessed '{delimiter}' as a delimiter")

                reader = csv.DictReader(f, delimiter=delimiter, skipinitialspace=True)

                data = list(reader)
                if callback is not None:
                    data = callback(data)

            ColorPrint.green(f"Successfully imported CSV data from {file_path}")

        except Exception as e:
            raise e

        return data

    @staticmethod
    def export_csv(
        data: List[Dict], file_path: str, delimiter: str = ",", append: bool = False
    ) -> None:
        """
        Helper function to export data into a CSV file.

        Args:
            data (list of dicts)     : The data to be exported.
            file_path (str)          : The path where the CSV file will be saved.
            delimiter (str, optional): The character used as a delimiter in the CSV file. Defaults to ",".
            append (bool, optional)  : Whether to append to an existing file or overwrite it.
        """

        if len(data) == 0:
            print("No data to export !")
            return

        full_path = os.path.join(os.getcwd(), file_path)

        try:
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
        file_path: str, delete_duplicates: bool = False, callback: Callable = None
    ) -> List[Any]:
        """
        Helper function to import a text file and optionally remove duplicates.

        Args:
            file_path (str)                   : The path to the text file.
            delete_duplicates (bool, optional): Whether to remove duplicate lines from the file.

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
    def export_txt(data: List[str], file_path: str, append: bool = False) -> None:
        """
        Helper function to export data into a text file.

        Args:
            data (list)             : The data to be exported as strings.
            file_path (str)         : The path where the text file will be saved.
            append (bool, optional) : Whether to append to an existing file or overwrite it.
        """

        if len(data) == 0:
            print("No data to export !")
            return

        full_path = os.path.join(os.getcwd(), file_path)

        try:
            mode = "a" if append else "w"
            with open(full_path, mode, encoding="utf-8", newline="") as f:
                for line in data:
                    f.write(line + "\n")

            ColorPrint.green(f"Successfully exported TXT data to {file_path}")

        except Exception as e:
            raise e


class FileType(Enum):
    """Enumeration of file types to be used by file connector"""

    CSV = {"import": FileHandler.import_csv, "export": FileHandler.export_csv}

    JSON = {"import": FileHandler.import_json, "export": FileHandler.export_json}

    TXT = {"import": FileHandler.import_txt, "export": FileHandler.export_txt}

    @property
    def f_import(self) -> Callable:
        """Get the import function for the file type.

        Returns:
            Callable: The import function as a callable object.
        """

        return self._value_["import"]

    @property
    def f_export(self) -> Callable:
        """Get the export function for the file type.

        Returns:
            Callable: The export function as a callable object.
        """

        return self._value_["export"]
