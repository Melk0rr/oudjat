from enum import Enum

from oudjat.utils.file import (
    export_csv,
    export_json,
    export_txt,
    import_csv,
    import_json,
    import_txt,
)


class FileType(Enum):
    """Enumeration of file types to be used by file connector"""

    CSV = {"import": import_csv, "export": export_csv}

    JSON = {"import": import_json, "export": export_json}

    TXT = {"import": import_txt, "export": export_txt}
