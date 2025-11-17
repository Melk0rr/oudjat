"""
A package dedicated to SentinelOne API connection.
"""

from .s1_connector import S1Connector
from .s1_endpoints import S1Endpoint

__all__ = [
    "S1Endpoint",
    "S1Connector",
]
