"""A module that describes common CVE data format accross CVE connectors (Nist, CVE.org, etc)."""

from datetime import datetime
from typing import TypedDict


class CVEDatesFmt(TypedDict):
    """
    A helper class that describes CVE date informations types.

    Attributes:
        published (str | datetime): the date the CVE was published
        updated (str | datetime): the last date the CVE was updated
    """

    published: str | datetime
    updated: str | datetime


class CVEVectorsFmt(TypedDict):
    """
    A helper class that describes CVE attack vector informations types.

    Attributes:
        vector_str (str)   : a string that describes the CVE attack vectors
        attack_vector (str): main CVE attack vector
    """

    vector_str: str
    attack_vector: str


class CVERequirementsFmt(TypedDict):
    """
    A helper class that describes CVE requirements types.

    Attributes:
        privileges_required (str): privileges required to exploit the CVE
        attack_requirements (str): any requirements to perform an attack using this CVE
    """

    privileges_required: str
    attack_requirements: str


class CVEMetricsFmt(TypedDict):
    """
    A helper class that describes CVE metrics types.

    Attributes:
        score (float)  : the score of the CVE
        version (float): the CVSS version used to assign the score
        severity (str) : the severity associated with the score
    """

    score: float
    version: float
    severity: str


class CVEDataFormat(TypedDict):
    """
    A helper class that describes shared CVE data format accross CVE connectors.

    Attributes:
        id (str)                         : CVE id (CVE-YYYY-XXXXX)
        dates (CVEDatesFmt)              : CVE dates format
        sources (list[str])              : sources of informations for the CVE
        status (str)                     : status of the CVE
        description (str)                : description of the vulnerability
        vectors (CVEVectorsFmt)          : CVE vector informations format
        requirements (CVERequirementsFmt): CVE exploitation requirements format
        metrics (CVEMetricsFmt)          : CVE metrics format
    """

    id: str
    dates: "CVEDatesFmt"
    sources: list[str]
    status: str
    description: str
    vectors: "CVEVectorsFmt"
    requirements: "CVERequirementsFmt"
    metrics: "CVEMetricsFmt"

