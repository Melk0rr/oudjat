import csv
import json
import os
import re
from typing import Any, Dict, List, Union


# INFO: JSON file functions
def import_json(file_path: str) -> Union[Dict, List]:
    """Helper function to import json data"""
    full_path = os.path.join(os.getcwd(), file_path)

    with open(full_path, "r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)

    return json_data


def export_json(data: List[Dict], file_path: str) -> None:
    """Exports data to a JSON file"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# INFO: CSV file functions
def import_csv(file_path: str, callback: object = None, delimiter: str = None) -> List[Dict]:
    """Helper function to import CSV content into a list of dictionaries"""
    full_path = os.path.join(os.getcwd(), file_path)

    with open(full_path, "r", encoding="utf-8", newline="") as f:
        # Try to guess the delimiter if none was specified
        if not delimiter:
            first_line = f.readline().strip("\n")
            f.seek(0)
            delimiter = re.findall(r"\W", first_line)[0]

            print(f"\nNo delimiter specified, guessed '{delimiter}' as a delimiter")

        reader = csv.DictReader(f, delimiter=delimiter, skipinitialspace=True)

        if callback:
            data = callback(list(reader))

        else:
            data = list(reader)

    return data


def export_csv(
    data: List[Dict], file_path: str, delimiter: str = ",", append: bool = False
) -> None:
    """Helper function to export data into a CSV file"""
    if len(data) == 0:
        print("No data to export !")
        return

    full_path = os.path.join(os.getcwd(), file_path)

    mode = "a" if append else "w"
    with open(full_path, mode, encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=delimiter)

        # Write csv headers if not in append mode
        if mode != "a":
            writer.writeheader()

        writer.writerows(data)


# INFO: TXT file functions
def import_txt(file_path: str, delete_duplicates: bool = False) -> List[Any]:
    """Helper function to import a txt file"""
    data = []
    full_path = os.path.join(os.getcwd(), file_path)

    with open(full_path, encoding="utf-8") as f:
        data = list(filter(None, f.read().split("\n")))

    if delete_duplicates:
        data = list(set(data))

    return data


def export_txt(data: List[str], file_path: str, append: bool = False) -> None:
    """Helper function to export data into a txt file"""

    if len(data) == 0:
        print("No data to export !")
        return

    full_path = os.path.join(os.getcwd(), file_path)

    mode = "a" if append else "w"
    with open(full_path, mode, encoding="utf-8", newline="") as f:
        for line in data:
            f.write(line + "\n")

