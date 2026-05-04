"""
A simple module that lists Sentinel One incident types.
"""

from enum import Enum


class S1IncidentType(Enum):
    """
    A simple enum to list S1 incident types.
    """

    THREAT = "threat"
    ALERT = "alert"
