"""A module that defines Windows releases."""

import os
from typing import TypeAlias, TypedDict

from oudjat.core.software.software_support import SoftwareReleaseSupportDict
from oudjat.utils.file_utils import FileUtils

PerVersionMSReleaseDict: TypeAlias = dict[str, "MSReleaseProps"]
PerOSMSReleaseDict: TypeAlias = dict[str, "PerVersionMSReleaseDict"]

ChannelDict: TypeAlias = dict[str, "SoftwareReleaseSupportDict"]

class MSReleaseProps(TypedDict):
    """
    A class to properly handle MS release attribute types.
    """

    os: str
    releaseLabel: str
    releaseDate: str
    latest: str
    link: str
    channels: "ChannelDict"

dirname = os.path.dirname(os.path.abspath(__file__))
WINDOWS_RELEASES: "PerOSMSReleaseDict" = FileUtils.import_json(f"{dirname}/releases.jsonc")[0]
