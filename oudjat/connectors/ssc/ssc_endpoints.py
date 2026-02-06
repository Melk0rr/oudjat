
"""
A helper module to list Security Score Card API endpoints.
"""

from enum import Enum
from typing import NamedTuple

from ..connector_methods import ConnectorMethod


class SSCEndpointsProps(NamedTuple):
    """
    A simple helper class to handle S1Endpoints property types.

    Attributes:
        path (str)              : The endpoint path
        method (ConnectorMethod): The method that should be used to connect to the endpoint
    """

    path: str
    method: "ConnectorMethod"


class SSCEndpoint(Enum):
    """
    An enumeration of the possible SentinelOne connection endpoints.
    """

    ISSUES = SSCEndpointsProps("/issues/{issueType}", ConnectorMethod.GET)
    SCORE_PLAN = SSCEndpointsProps("/score-plans/by-target/{level}", ConnectorMethod.GET)

    @property
    def path(self) -> str:
        """
        Return the path attribute of the S1Endpoint element.

        Returns:
            str: The path string of the endpoint
        """

        return self._value_.path

    @property
    def method(self) -> "ConnectorMethod":
        """
        Return the method attribute of the endpoint.

        Returns:
            ConnectorMethod: The connector method that must be used to interract with the endpoint
        """

        return self._value_.method
