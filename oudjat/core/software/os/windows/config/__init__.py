"""A Windows sub package dedicated to import windows releases configs."""

import os

from oudjat.core.software.software_release import SoftwareReleaseImportDict
from oudjat.utils.file_utils import FileUtils

dirname = os.path.dirname(os.path.abspath(__file__))

WINDOWS_RELEASES: "SoftwareReleaseImportDict" = FileUtils.import_json(f"{dirname}/windows.json")[0]
WINDOWS_SERVER_RELEASES: "SoftwareReleaseImportDict" = FileUtils.import_json(f"{dirname}/windowsserver.json")[0]

__all__ = ["WINDOWS_RELEASES", "WINDOWS_SERVER_RELEASES"]
