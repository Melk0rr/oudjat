from enum import Enum
from typing import List


class CybereasonEndpoint(Enum):
    """Cybereason API endpoint attributes"""

    SENSORS = {
        "path": "/rest/sensors/query",
        "method": "POST",
        "limit": 30000,
        "attributes": [
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
    }

    SENSORS_ACTION = {
        "path": "/rest/sensors/action",
        "method": "POST"
    }

    MALWARES = {
        "path": "/rest/malware/query",
        "method": "POST",
        "limit": 1000,
        "attributes": [
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
    }

    POLICIES = {
        "path": "rest/policies",
        "method": "POST",
    }

    FILES = {
        "path": "/rest/sensors/action/fileSearch",
        "method": "POST",
        "limit": 30000,
        "attributes": [],
    }

    USERS = {
        "path": "/rest/users",
        "method": "GET",
        "limit": 200,
        "attributes": ["creationTime", "groups", "lastUpdateTime", "locked", "roles", "username"],
    }

    GROUPS = {
        "path": "/rest/groups",
        "method": "GET",
        "limit": 300,
        "attributes": ["creationTime", "description", "id", "lastUpdate", "name"],
    }

    @property
    def path(self) -> str:
        """
        Returns a CybereasonEndpoint element path

        Returns:
            str: the path of the endpoint
        """

        return self._value_["path"]

    @property
    def method(self) -> str:
        """
        Returns a CybereasonEndpoint element HTTP method

        Returns:
            str: the HTTP method to use for the endpoint
        """

        return self._value_["method"]

    @property
    def limit(self) -> str:
        """
        Returns a CybereasonEndpoint element search results limit

        Returns:
            int: the limit number of search results
        """

        return self._value_["limit"]

    @property
    def attributes(self) -> List[str]:
        """
        Returns a CybereasonEndpoint element search result attributes

        Returns:
            List[str]: the list of attributes to return from requesting the endpoint if relevent
        """

        return self._value_["attributes"]
