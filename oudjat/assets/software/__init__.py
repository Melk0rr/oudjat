from .software import Software, SoftwareType
from .software_edition import SoftwareEdition, SoftwareEditionDict
from .software_release import SoftwareRelease, SoftwareReleaseDict
from .software_support import SoftwareReleaseSupport, SoftwareReleaseSupportList

__all__ = [
    "Software",
    "SoftwareType",
    "SoftwareEdition",
    "SoftwareEditionDict",
    "SoftwareRelease",
    "SoftwareReleaseDict",
    "SoftwareReleaseSupport",
    "SoftwareReleaseSupportList",
]

# TODO: see if releases can be handled in a simpler way -> no imbricated SoftwareReleaseDict
