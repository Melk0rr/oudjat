from enum import Enum

from oudjat.utils import import_csv, import_json, import_txt

class FileType(Enum):
  """ Enumeration of file types to be used by file connector """
  CSV = {
    "import": import_csv
  }

  JSON = {
    "import": import_json
  }

  TXT = {
    "import": import_txt
  }