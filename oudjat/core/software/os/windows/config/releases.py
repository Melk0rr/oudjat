"""A module that defines Windows releases."""

import os
from typing import TypeAlias, TypedDict

from oudjat.utils.file_utils import FileUtils

# TODO: Rework JSON structure and SoftwareReleaseDict

PerVersionMSReleaseDict: TypeAlias = dict[str, "MSReleaseProps"]
PerOSMSReleaseDict: TypeAlias = dict[str, "PerVersionMSReleaseDict"]

class MSSupportProps(TypedDict):
    """
    A class to properly handle MS support attribute types.

    Attributes:
        eos (str)       : Base end of support date
        eol (str)       : End of life / end of security support
        esu (str | None): Extended security support date
        lts (bool)      : Does the channel include Long Time Support
    """

    activeSupport: str
    securitySupport: str
    extendedSecuritySupport: str | None
    lts: bool

ChannelDict: TypeAlias = dict[str, "MSSupportProps"]

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
