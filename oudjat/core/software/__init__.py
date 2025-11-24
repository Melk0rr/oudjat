"""An asset sub package that focuses on software."""

from .software import Software, SoftwareType
from .software_edition import SoftwareEdition, SoftwareEditionDict
from .software_release import SoftwareRelease, SoftwareReleaseDict
from .software_release_version import SoftwareReleaseStage, SoftwareReleaseVersion
from .software_support import SoftwareReleaseSupport, SoftwareReleaseSupportList

__all__ = [
    "Software",
    "SoftwareType",
    "SoftwareEdition",
    "SoftwareEditionDict",
    "SoftwareRelease",
    "SoftwareReleaseDict",
    "SoftwareReleaseStage",
    "SoftwareReleaseVersion",
    "SoftwareReleaseSupport",
    "SoftwareReleaseSupportList",
]
