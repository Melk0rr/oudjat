from enum import Enum

class CybereasonEndpoints(Enum):
  """ Cybereason API endpoint attributes """
  SENSORS = {
    "endpoint": "/rest/sensors/query",
    "method": "POST",
    "limit": 30000,
    "attributes": [
      "fqdn",
      "machineName",
      "internalIpAddress",
      "externalIpAddress",
      "ransomwareStatus",
      "preventionStatus",
      "isolated",
      "status",
      "osVersionType",
      "version",
      "amStatus",
      "avDbVersion",
      "avDbLastUpdateTime",
      "disconnectionTime",
      "policyName",
      "groupName",
      "upTime"
    ]
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
      "malwareDataModel"
    ]
  }

  USERS = {
    "endpoint": "/rest/users",
    "method": "GET",
    "limit": 200,
    "attributes": [
      "creationTime",
      "groups",
      "lastUpdateTime",
      "locked",
      "roles",
      "username"
    ]
  }

  GROUPS = {
    "endpoint": "/rest/groups",
    "method": "GET",
    "limit": 300,
    "attributes": [
      "creationTime",
      "description",
      "id",
      "lastUpdate",
      "name"
    ]
  }