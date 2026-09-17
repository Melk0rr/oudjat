"""A package dedicated to various EDR connection."""

from .sentinelone.s1_analyst_verdicts import S1AnalystVerdict
from .sentinelone.s1_connector import S1Connector
from .sentinelone.s1_endpoints import S1Endpoint

__all__ = [
    "S1AnalystVerdict",
    "S1Connector",
    "S1Endpoint",
]
