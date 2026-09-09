"""An asset sub package that focuses on software."""

from .definitions import STAGE_REG, VERSION_REG
from .software import Software, SoftwareType
from .software_edition import SoftwareEdition, SoftwareEditionDict
from .software_release import SoftwareRelease, SoftwareRelVersionDict
from .software_release_version import SoftwareReleaseStage, SoftwareReleaseVersion
from .software_support import (
    Support,
    SupportDictProps,
    SupportPhase,
    SupportPhaseProps,
    SupportPhaseType,
    SupportStatus,
)

__all__ = [
    "STAGE_REG",
    "VERSION_REG",
    "Software",
    "SoftwareEdition",
    "SoftwareEditionDict",
    "SoftwareRelVersionDict",
    "SoftwareRelease",
    "SoftwareReleaseStage",
    "SoftwareReleaseVersion",
    "SoftwareType",
    "SupportDict",
    "SupportDictProps",
    "SupportPhase",
    "SupportPhaseProps",
    "SupportPhaseType",
    "SupportStatus",
]
