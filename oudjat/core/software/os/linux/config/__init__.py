"""A Linux sub package dedicated to import linux releases configs."""

import os

from oudjat.core.software.software_release import SoftwareReleaseImportDict
from oudjat.utils.file_utils import FileUtils

dirname = os.path.dirname(os.path.abspath(__file__))

RHEL_RELEASES: "SoftwareReleaseImportDict" = FileUtils.import_json(f"{dirname}/rhel.json")[0]

__all__ = ["RHEL_RELEASES"]

