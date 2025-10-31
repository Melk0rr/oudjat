"""A module to handle Cybereason API endpoints."""

from enum import Enum
from typing import NamedTuple

from ...connector_methods import ConnectorMethod


class CybereasonEndpointProps(NamedTuple):
    """
    A helper class to properly handle CybereasonEndpoint types.

    Attributes:
        path (str): the path to the endpoint
        method (ConnectorMethod): HTTP method used to access the endpoint
        limit (int | None): default result limit number
        attributes (list[str] | None): list of default attributes to retrieve from endpoint
    """

    path: str
    method: ConnectorMethod
    limit: int | None
    attributes: list[str]


class CybereasonEndpoint(Enum):
    """Cybereason API endpoint attributes."""

    SENSORS = CybereasonEndpointProps(
        path="/rest/sensors/query",
        method=ConnectorMethod.POST,
        limit=30000,
        attributes=[
            "amStatus",
            "avDbLastUpdateTime",
            "avDbVersion",
            "disconnectionTime",
            "externalIpAddress",
            "fqdn",
            "groupName",
            "internalIpAddress",
            "isolated",
            "machineName",
            "osVersionType",
            "policyName",
            "preventionStatus",
            "ransomwareStatus",
            "sensorId",
            "serialNumber",
            "status",
            "upTime",
            "version",
        ],
    )

    SENSORS_ACTION = CybereasonEndpointProps(
        path="/rest/sensors/action",
        method=ConnectorMethod.POST,
        limit=1000,
        attributes=[],
    )

    MALWARES = CybereasonEndpointProps(
        path="/rest/malware/query",
        method=ConnectorMethod.POST,
        limit=1000,
        attributes=[
            "timestamp",
            "name",
            "type",
            "elementType",
            "machineName",
            "status",
            "needsAttention",
            "detectionEngine",
            "malwareDataModel",
        ],
    )

    POLICIES = CybereasonEndpointProps(
        path="rest/policies", method=ConnectorMethod.POST, limit=1000, attributes=[]
    )

    FILES = CybereasonEndpointProps(
        path="/rest/sensors/action/fileSearch",
        method=ConnectorMethod.POST,
        limit=30000,
        attributes=[],
    )

    USERS = CybereasonEndpointProps(
        path="/rest/users",
        method=ConnectorMethod.GET,
        limit=200,
        attributes=["creationTime", "groups", "lastUpdateTime", "locked", "roles", "username"],
    )

    GROUPS = CybereasonEndpointProps(
        path="/rest/groups",
        method=ConnectorMethod.GET,
        limit=300,
        attributes=["creationTime", "description", "id", "lastUpdate", "name"],
    )

    @property
    def path(self) -> str:
        """
        Return a CybereasonEndpoint element path.

        Returns:
            str: the path of the endpoint
        """

        return self._value_.path

    @property
    def method(self) -> "ConnectorMethod":
        """
        Return a CybereasonEndpoint element HTTP method.

        Returns:
            str: the HTTP method to use for the endpoint
        """

        return self._value_.method

    @property
    def limit(self) -> int:
        """
        Return a CybereasonEndpoint element search results limit.

        Returns:
            int: the limit number of search results
        """

        return self._value_.limit or 1000

    @property
    def attributes(self) -> list[str]:
        """
        Return a CybereasonEndpoint element search result attributes.

        Returns:
            List[str]: the list of attributes to return from requesting the endpoint if relevent
        """

        return self._value_.attributes
