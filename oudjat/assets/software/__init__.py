"""An asset sub package that focuses on software."""

from .software import Software, SoftwareRelease, SoftwareReleaseDict, SoftwareType
from .software_edition import SoftwareEdition, SoftwareEditionDict
from .software_release_version import SoftwareReleaseStage, SoftwareReleaseVersion
from .software_support import SoftwareReleaseSupport, SoftwareReleaseSupportList

__all__ = [
    "Software",
    "SoftwareType",
    "SoftwareEdition",
    "SoftwareEditionDict",
    "SoftwareRelease",
    "SoftwareReleaseStage",
    "SoftwareReleaseVersion",
    "SoftwareReleaseDict",
    "SoftwareReleaseSupport",
    "SoftwareReleaseSupportList",
]

# TODO: see if releases can be handled in a simpler way -> no imbricated SoftwareReleaseDict
