"""
A helper module to list SentinelOne API endpoints.
"""

from dataclasses import dataclass
from enum import Enum
from typing import override

from ...connector_methods import ConnectorMethod


@dataclass
class S1EndpointsProps:
    """
    A simple helper class to handle S1Endpoints property types.

    Attributes:
        path (str)              : The endpoint path
        method (ConnectorMethod): The method that should be used to connect to the endpoint
    """

    path: str
    method: "ConnectorMethod"
    description: str | None = None


class S1Endpoint(Enum):
    """
    An enumeration of the possible SentinelOne connection endpoints.
    """

    # ======== Accounts ========
    ACCOUNTS = S1EndpointsProps(
        "/web/api/v2.1/accounts",
        ConnectorMethod.GET,
        "Retrieve accounts data",
    )

    # ======== Agents ========
    AGENTS_ACTIONS_DECOMMISSION = S1EndpointsProps(
        "/web/api/v2.1/agents/actions/decommission",
        ConnectorMethod.POST,
        "Remove agent from the management console",
    )
    AGENTS_COUNT = S1EndpointsProps(
        "/web/api/v2.1/agents/count",
        ConnectorMethod.GET,
        "Count agents",
    )
    AGENTS = S1EndpointsProps(
        "/web/api/v2.1/agents",
        ConnectorMethod.GET,
        "Retrieve agents details",
    )
    AGENTS_EXPORT = S1EndpointsProps(
        "/web/api/v2.1/export/agents",
        ConnectorMethod.GET,
        "Export agents data to CSV compatible format",
    )
    AGENTS_ACTIONS_MOVE_TO_SITE = S1EndpointsProps(
        "/web/api/v2.1/agents/actions/move-to-site",
        ConnectorMethod.POST,
        "Move agents to a site",
    )

    # ======== Alerts ========
    ALERTS_ANALYST_VERDICT = S1EndpointsProps(
        "/web/api/v2.1/cloud-detection/alerts/analyst-verdict",
        ConnectorMethod.POST,
        "Change alerts analyst verdict",
    )
    ALERTS_INCIDENT = S1EndpointsProps(
        "/web/api/v2.1/cloud-detection/alerts/incident",
        ConnectorMethod.POST,
        "Change alerts status",
    )

    # ======== Applications ========
    APPLICATIONS_INVENTORY = S1EndpointsProps(
        "/web/api/v2.1/application-management/inventory",
        ConnectorMethod.GET,
        "Retrieve application inventory grouped by application and vendor",
    )
    APPLICATIONS_INVENTORY_ENDPOINTS = S1EndpointsProps(
        "/web/api/v2.1/application-management/inventory/endpoints",
        ConnectorMethod.GET,
        "Retrieve endpoints an application is installed on",
    )
    APPLICATIONS_CVES = S1EndpointsProps(
        "/web/api/v2.1/application-management/risks",
        ConnectorMethod.GET,
        "Retrieve CVEs vulnerability data",
    )
    APPLICATIONS_APP_CVES = S1EndpointsProps(
        "/web/api/v2.1/application-management/risks/cves",
        ConnectorMethod.GET,
        "Retrieve applications CVE data",
    )
    APPLICATIONS_WITH_RISKS = S1EndpointsProps(
        "/web/api/v2.1/application-management/risks/applications",
        ConnectorMethod.GET,
        "Retrieve applications with risks",
    )

    # ======== Groups ========
    GROUPS = S1EndpointsProps(
        "/web/api/v2.1/groups",
        ConnectorMethod.GET,
        "Retrieve groups data",
    )
    GROUPS_UPDATE = S1EndpointsProps(
        "/web/api/v2.1/groups/{groupId}",
        ConnectorMethod.PUT,
        "Update properties of a group",
    )
    GROUPS_MOVE_AGENTS = S1EndpointsProps(
        "/web/api/v2.1/groups/{groupId}/move-agents",
        ConnectorMethod.PUT,
        "Move agents to a group",
    )

    # ======== Policies ========
    ACCOUNTS_POLICY = S1EndpointsProps(
        "/web/api/v2.1/accounts/{accountId}/policy",
        ConnectorMethod.GET,
        "Retrieve the policy of an account",
    )
    GROUPS_POLICY = S1EndpointsProps(
        "/web/api/v2.1/groups/{groupId}/policy",
        ConnectorMethod.GET,
        "Retrieve a group policy",
    )
    SITES_POLICY = S1EndpointsProps(
        "/web/api/v2.1/sites/{siteId}/policy",
        ConnectorMethod.GET,
        "Retrieve the policy of a site",
    )
    GROUPS_POLICY_UPDATE = S1EndpointsProps(
        "/web/api/v2.1/groups/{groupId}/policy",
        ConnectorMethod.PUT,
        "Update the policy of a group",
    )
    SITES_POLICY_UPDATE = S1EndpointsProps(
        "/web/api/v2.1/sites/{siteId}/policy",
        ConnectorMethod.PUT,
        "Update the policy of a site",
    )

    # ======== RBAC ========
    RBAC_ROLES = S1EndpointsProps(
        "/web/api/v2.1/rbac/roles",
        ConnectorMethod.GET,
        "Retrieve roles assigned users",
    )
    RBAC_ROLE = S1EndpointsProps(
        "/web/api/v2.1/rbac/role/{roleId}",
        ConnectorMethod.GET,
        "Retrieve a specific role data",
    )

    # ======== Sites ========
    SITES_BY_ID = S1EndpointsProps(
        "/web/api/v2.1/sites/{siteId}",
        ConnectorMethod.GET,
        "Retrieve data of a sppecific site",
    )
    SITES = S1EndpointsProps(
        "/web/api/v2.1/sites",
        ConnectorMethod.GET,
        "Retrieve sites data",
    )

    # ======== Threats ========
    THREATS = S1EndpointsProps(
        "/web/api/v2.1/threats",
        ConnectorMethod.GET,
        "Retrieve threats data",
    )
    THREATS_ANALYST_VERDICT = S1EndpointsProps(
        "/web/api/v2.1/threats/analyst-verdict",
        ConnectorMethod.POST,
        "Update threats analyst verdict",
    )
    THREATS_INCIDENT = S1EndpointsProps(
        "/web/api/v2.1/threats/incident",
        ConnectorMethod.POST,
        "Update threats analyst verdict and status",
    )

    # ======== Users ========
    USERS = S1EndpointsProps(
        "/web/api/v2.1/users",
        ConnectorMethod.GET,
        "Retrieve users",
    )
    USERS_LOGIN = S1EndpointsProps(
        "/web/api/v2.1/users/login",
        ConnectorMethod.POST,
        "Authenticate a user by username/password",
    )
    USERS_LOGIN_BY_API_TOKEN = S1EndpointsProps(
        "/web/api/v2.1/users/login/by-api-token",
        ConnectorMethod.POST,
        "Authenticate a user by api-token",
    )
    USERS_LOGIN_BY_TOKEN = S1EndpointsProps(
        "/web/api/v2.1/users/login/by-token",
        ConnectorMethod.POST,
        "Log in with user token",
    )
    USERS_LOGOUT = S1EndpointsProps(
        "/web/api/v2.1/users/logout",
        ConnectorMethod.POST,
        "Log out the authenticated user",
    )
    USERS_CHANGE_PASSWORD = S1EndpointsProps(
        "/web/api/v2.1/users/change-password",
        ConnectorMethod.POST,
        "Change the user password",
    )

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

    @property
    def description(self) -> str | None:
        """
        Return the description of the S1Endpoint.

        Returns:
            str | None: The description of the endpoint if any
        """

        return self._value_.description

    @override
    def __str__(self) -> str:
        """
        Convert the S1Endpoint into a string.

        Returns:
            str: A string representation of the endpoint
        """

        return self._name_
