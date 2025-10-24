"""
A helper module to list SentinelOne API endpoints.
"""

from enum import Enum
from typing import NamedTuple

from ...connector_methods import ConnectorMethod


class S1EndpointsProps(NamedTuple):
    """
    A simple helper class to handle S1Endpoints property types.

    Attributes:
        path (str)              : The endpoint path
        method (ConnectorMethod): The method that should be used to connect to the endpoint
    """

    path: str
    method: "ConnectorMethod"


class S1Endpoints(Enum):
    """
    An enumeration of the possible SentinelOne connection endpoints.
    """

    AGENTS_ACTIONS_DECOMMISSION = S1EndpointsProps(
        "/web/api/v2.1/agents/actions/decommission", ConnectorMethod.POST
    )
    AGENTS_COUNT = S1EndpointsProps("/web/api/v2.1/agents/count", ConnectorMethod.GET)
    AGENTS = S1EndpointsProps("/web/api/v2.1/agents", ConnectorMethod.GET)
    AGENTS_ACTIONS_MOVE_TO_SITE = S1EndpointsProps(
        "/web/api/v2.1/agents/actions/move-to-site", ConnectorMethod.POST
    )
    APPLICATIONS_INVENTORY = S1EndpointsProps(
        "/web/api/v2.1/application-management/inventory/endpoints", ConnectorMethod.GET
    )
    APPLICATIONS_CVES = S1EndpointsProps(
        "/web/api/v2.1/application-management/risks/cves", ConnectorMethod.GET
    )
    GROUPS = S1EndpointsProps("/web/api/v2.1/groups", ConnectorMethod.GET)
    GROUPS_MOVE_AGENTS = S1EndpointsProps(
        "/web/api/v2.1/groups/{groupId}/move-agents", ConnectorMethod.PUT
    )
    CLOUD_DETECTION_ALERTS = S1EndpointsProps(
        "/web/api/v2.1/cloud-detection/alerts", ConnectorMethod.GET
    )
    ACCOUNTS_POLICY = S1EndpointsProps(
        "/web/api/v2.1/accounts/{account_id}/policy", ConnectorMethod.GET
    )
    TENANT_POLICY = S1EndpointsProps("/web/api/v2.1/tenant/policy", ConnectorMethod.GET)
    GROUPS_POLICY = S1EndpointsProps("/web/api/v2.1/groups/{group_id}/policy", ConnectorMethod.GET)
    SITES_POLICY = S1EndpointsProps("/web/api/v2.1/sites/{site_id}/policy", ConnectorMethod.GET)
    RBAC_ROLES = S1EndpointsProps("/web/api/v2.1/rbac/roles", ConnectorMethod.GET)
    RBAC_ROLE = S1EndpointsProps("/web/api/v2.1/rbac/role/{role_id}", ConnectorMethod.GET)
    SITES_ID = S1EndpointsProps("/web/api/v2.1/sites/{site_id}", ConnectorMethod.GET)
    SITES = S1EndpointsProps("/web/api/v2.1/sites", ConnectorMethod.GET)
    UPDATE_AGENT_DOWNLOAD = S1EndpointsProps(
        "/web/api/v2.1/update/agent/download/{site_id}/{package_id}", ConnectorMethod.GET
    )
    UPDATE_AGENT_PACKAGES = S1EndpointsProps(
        "/web/api/v2.1/update/agent/packages", ConnectorMethod.GET
    )
    USERS_API_TOKEN_DETAILS_BY_ID = S1EndpointsProps(
        "/web/api/v2.1/users/{user_id}/api-token-details", ConnectorMethod.GET
    )
    USERS_API_TOKEN_DETAILS = S1EndpointsProps(
        "/web/api/v2.1/users/api-token-details", ConnectorMethod.GET
    )
    USERS_AUTH_APP = S1EndpointsProps("/web/api/v2.1/users/auth/app", ConnectorMethod.POST)
    USERS_LOGIN_SSO_SAML2 = S1EndpointsProps(
        "/web/api/v2.1/users/login/sso-saml2/{scope_id}", ConnectorMethod.POST
    )
    USERS_AUTH_RECOVERY_CODE = S1EndpointsProps(
        "/web/api/v2.1/users/auth/recovery-code", ConnectorMethod.POST
    )
    USERS_CHANGE_PASSWORD = S1EndpointsProps(
        "/web/api/v2.1/users/change-password", ConnectorMethod.POST
    )
    USERS = S1EndpointsProps("/web/api/v2.1/users", ConnectorMethod.GET)
    USERS_LOGIN = S1EndpointsProps("/web/api/v2.1/users/login", ConnectorMethod.POST)
    USERS_LOGIN_BY_API_TOKEN = S1EndpointsProps(
        "/web/api/v2.1/users/login/by-api-token", ConnectorMethod.POST
    )
    USERS_LOGIN_BY_TOKEN = S1EndpointsProps(
        "/web/api/v2.1/users/login/by-token", ConnectorMethod.POST
    )
    USERS_LOGOUT = S1EndpointsProps("/web/api/v2.1/users/logout", ConnectorMethod.POST)
    USERS_GENERATE_API_TOKEN = S1EndpointsProps(
        "/web/api/v2.1/users/generate-api-token", ConnectorMethod.POST
    )
    USERS_REVOKE_API_TOKEN = S1EndpointsProps(
        "/web/api/v2.1/users/revoke-api-token", ConnectorMethod.POST
    )
    USERS_ONBOARDING_SEND_VERIFICATION_EMAIL = S1EndpointsProps(
        "/web/api/v2.1/users/onboarding/send-verification-email",
        ConnectorMethod.POST,
    )
    USER_BY_TOKEN = S1EndpointsProps("/web/api/v2.1/user", ConnectorMethod.GET)
    SYSTEM_STATUS_CACHE = S1EndpointsProps("/web/api/v2.1/system/status/cache", ConnectorMethod.GET)
    SYSTEM_STATUS_DB = S1EndpointsProps("/web/api/v2.1/system/status/db", ConnectorMethod.GET)
    SYSTEM_CONFIGURATION = S1EndpointsProps(
        "/web/api/v2.1/system/configuration", ConnectorMethod.GET
    )
    SYSTEM_CONFIGURATION_SET = S1EndpointsProps(
        "/web/api/v2.1/system/configuration", ConnectorMethod.PUT
    )
    SYSTEM_INFO = S1EndpointsProps("/web/api/v2.1/system/info", ConnectorMethod.GET)
    SYSTEM_STATUS = S1EndpointsProps("/web/api/v2.1/system/status", ConnectorMethod.GET)
    THREATS = S1EndpointsProps("/web/api/v2.1/threats", ConnectorMethod.GET)
