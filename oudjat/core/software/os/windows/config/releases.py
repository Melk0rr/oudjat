"""A module that defines Windows releases."""

import os
from typing import TypeAlias, TypedDict

from oudjat.utils.file_utils import FileUtils

# TODO: Rework JSON structure and SoftwareReleaseDict

PerEditionMSReleaseDict: TypeAlias = dict[str, "MSReleaseProps"]
PerVersionMSReleaseDict: TypeAlias = dict[str, "PerEditionMSReleaseDict"]
PerOSMSReleaseDict: TypeAlias = dict[str, "PerVersionMSReleaseDict"]

class MSReleaseProps(TypedDict):
    """A class to properly handle MS release types."""

    os: str
    releaseLabel: str
    releaseDate: str
    support: str
    eol: str
    lts: bool
    latest: str
    link: str
    edition: str

dirname = os.path.dirname(os.path.abspath(__file__))
WINDOWS_RELEASES: "PerOSMSReleaseDict" = FileUtils.import_json(f"{dirname}/releases.jsonc")[0]
