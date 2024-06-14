import os
import re
import csv
import json

# JSON file functions
def import_json(file_path):
  """ Helper function to import json data """
  full_path = os.path.join(os.getcwd(), file_path)

  with open(full_path) as json_file:
    json_data = json.load(json_file)
    
  return json_data

# CSV file functions
def export_csv(data, file_path, delimiter=',', append=False):
  """ Helper function to export data into a CSV file """
  if len(data) == 0:
    print("No data to export !")
    return

  full_path = os.path.join(os.getcwd(), file_path)

  mode = "a" if append else "w"
  with open(full_path, mode, encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=delimiter)
    writer.writeheader()
    writer.writerows(data)

def import_csv(file_path, callback=None, delimiter=None):
  """ Helper function to import CSV content into a list of dictionaries """
  full_path = os.path.join(os.getcwd(), file_path)

  with open(full_path, "r", encoding="utf-8", newline="") as f:
    # Try to guess the delimiter if none was specified
    if not delimiter:
      first_line = f.readline().strip("\n")
      f.seek(0)
      delimiter = re.findall(r'\W', first_line)[0]

      print(f"\nNo delimiter specified, guessed '{delimiter}' as a delimiter")

    reader = csv.DictReader(f, delimiter=delimiter, skipinitialspace=True)
    
    if callback:
      data = callback(list(reader))

    else:
      data = [row for row in list(reader)]

  return data