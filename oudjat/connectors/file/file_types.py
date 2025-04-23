from enum import Enum
from typing import Callable

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
