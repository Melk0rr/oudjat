from enum import Enum


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

