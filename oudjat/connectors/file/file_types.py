from enum import Enum

from oudjat.utils.file import import_csv, import_json, import_txt

class FileTypes(Enum):
  """ Enumeration of file types to be used by file connector """
  CSV = {
    "import_function": import_csv
  }

  JSON = {
    "import_function": import_json
  }

  TXT = {
    "import_function": import_txt
  }