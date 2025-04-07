from enum import Enum


class CybereasonEndpoint(Enum):
    """Cybereason API endpoint attributes"""

    SENSORS = {
        "endpoint": "/rest/sensors/query",
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
        "endpoint": "/rest/sensors/action",
        "method": "POST"
    }

    MALWARES = {
        "endpoint": "/rest/malware/query",
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
        "endpoint": "rest/policies",
        "method": "POST",
    }

    FILES = {
        "endpoint": "/rest/sensors/action/fileSearch",
        "method": "POST",
        "limit": 30000,
        "attributes": [],
    }

    USERS = {
        "endpoint": "/rest/users",
        "method": "GET",
        "limit": 200,
        "attributes": ["creationTime", "groups", "lastUpdateTime", "locked", "roles", "username"],
    }

    GROUPS = {
        "endpoint": "/rest/groups",
        "method": "GET",
        "limit": 300,
        "attributes": ["creationTime", "description", "id", "lastUpdate", "name"],
    }

