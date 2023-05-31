import os
import csv

def export_2_csv(data, file_path, delimiter=','):
  """ Helper function to export data into a CSV file """
  full_path = os.path.join(os.getcwd(), file_path)

  with open(full_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=delimiter)
    writer.writeheader()
    writer.writerows(data)

def import_csv(file_path, callback, delimiter=','):
  """ Helper function to import CSV content into a list of dictionaries """
  full_path = os.path.join(os.getcwd(), file_path)

  with open(full_path, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f, delimiter=delimiter)
    data = callback(reader)

  return data
