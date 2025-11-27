"""
A module that handles SentinelOne API connection and interactions.
"""

import logging
import re
from typing import Any, override
from urllib.parse import ParseResult, urlparse

import requests

from oudjat.utils.context import Context
from oudjat.utils.credentials import NoCredentialsError
from oudjat.utils.types import DataType, StrType

from ... import Connector
from .exceptions import SentinelOneAPIConnectionError
from .s1_endpoints import S1Endpoint


class S1Connector(Connector):
    """
    A class that handles SentinelOne API connections and interactions.
    """

    # ****************************************************************
    # Attributes & Constructors
    def __init__(
        self,
        target: str,
        username: str | None = None,
        api_token: str | None = None,
        port: int = 443,
    ) -> None:
        """
        Create a new instance of S1Connector.

        Args:
            target (str)   : SentinelOne URL
            username (str) : Username to use for the connection
            api_token (str): API token. Stored as the connector credentials.password
            port (int)     : Port number used for the connection
        """

        self.logger: "logging.Logger" = logging.getLogger(__name__)

        scheme = "http"
        if port == 443:
            scheme += "s"

        # Inject protocol if not found
        if not re.match(r"http(s?):", target):
            target = f"{scheme}://{target}"

        self._target: "ParseResult"
        super().__init__(target=urlparse(target), username=username, password=api_token)

        self._connection: "requests.Session | None" = None
        self._DEFAULT_HEADERS: dict[str, str] = {"Content-Type": "application/json"}

    # ****************************************************************
    # Methods

    @property
    def _api_token(self) -> str | None:
        """
        Return the connector api token.

        Just an aliad for the connector password.

        Returns:
            str | None: The connector password string if set. Else, None
        """

        return self._credentials.password if self._credentials is not None else None

    @property
    def _headers(self) -> dict[str, Any]:
        """
        Return the correct headers based on whether the connection was initialized or not.

        Returns:
            dict[str, Any]: Headers as a dictionary
        """

        headers = self._DEFAULT_HEADERS
        if self._connection:
            headers["Authorization"] = f"Token {self._connection}"

        return headers

    def _unify_str_list(self, str_list: StrType) -> str:
        """
        Unify API query string array parameters.

        If the parameter is a string, the function return it untouched.
        If the parameter is a list of strings, the function return it as a joined string.

        Args:
            str_list (str | list[str]): Parameter to unify

        Returns:
            str: Unified parameter as a string
        """

        return ",".join(str_list) if isinstance(str_list, list) else str_list

    @override
    def connect(self) -> None:
        """
        Connect to the target.
        """

        context = Context()

        if self._credentials is None:
            raise NoCredentialsError(f"{context}::No password provided")

        if not self._connection:
            self.logger.info(f"{context}::Connecting to {self._target.netloc} with user API token")

            if self._api_token:
                try:
                    data = self.login_by_api_token()
                    self._connection = data[0]["token"]

                except SentinelOneAPIConnectionError as e:
                    raise SentinelOneAPIConnectionError(f"{context}::{e}")

            else:
                raise NoCredentialsError(f"{context}::No API token provided")

            self.logger.info(f"{context}::Connected to {self._target.netloc}")
        else:
            self.logger.warning(
                f"{context}::Connection to {self._target.netloc} is already initialized."
            )

    @override
    def fetch(
        self,
        endpoint: "S1Endpoint",
        payload: dict[str, Any],
        attributes: list[str] | None = None,
        path_fmt: dict[str, str] | None = None,
    ) -> "DataType":
        """
        Perform a search query through the API to retrieve data based on provided endpoint and .

        Args:
            endpoint (S1Endpoints)          : SentinelOne endpoint the query payload will be send to
            attributes (list[str] | None)   : List of attributes to keep per elements
            payload (dict[str, Any] | None) : Payload to send to the provided endpoint
            path_fmt (dict[str, Any] | None): A dictionary of variable names that will be replaced in the endpoint path

        Returns:
            DataType: list of retrieved elements
        """

        context = Context()

        res = []
        next_cursor = None

        endpoint_path = endpoint.path
        if path_fmt:
            endpoint_path = endpoint_path.format(**path_fmt)

        self.logger.debug(f"{context}::{endpoint} > {payload}")
        while True:
            if next_cursor:
                payload["cursor"] = next_cursor

            r_params = {
                "url": f"{self._target.geturl()}{endpoint_path}",
                "headers": self._headers,
                "json": payload,
            }

            if endpoint.method.name == "GET":
                r_params["params"] = r_params.pop("json")

            req = endpoint.method(**r_params)
            req_json = req.json()

            if "data" in req_json:
                if isinstance(req_json["data"], list):
                    res.extend(req_json["data"])

                else:
                    res.append(req_json["data"])

            self.logger.debug(f"{context}::{endpoint} > {req_json}")

            if req.status_code != 200:
                raise SentinelOneAPIConnectionError(
                    f"{context}::An error occured while fetching data from {endpoint}\n{req_json['errors']}"
                )

            next_cursor = req_json.get("pagination", {}).get("nextCursor", None)
            if not next_cursor:
                break

        return res

    # ****************************************************************
    # Methods: Agents

    def agents(
        self,
        site_ids: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
        infected: bool = False,
        net_statuses: "StrType | None" = None,
    ) -> DataType:
        """
        Return the agents based on the provided filter.

        Possible response messages
        200 - Success
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry.

        Args:
            site_ids (str | list[str] | None)    : List of site ids to filter
            payload (dict[str, Any])             : Payload to send to the endpoint
            infected (bool)                      : Whether to only include agents with at least one active threat
            net_statuses (str | list[str] | None): Network statuses to filter

        Returns:
            DataType: response data with agentID
        """

        if payload is None:
            payload = {}

        if site_ids is not None:
            payload["siteIds"] = self._unify_str_list(site_ids)

        if infected:
            payload["infected"] = True

        if net_statuses is not None:
            payload["netStatuses"] = self._unify_str_list(net_statuses)

        return self.fetch(endpoint=S1Endpoint.AGENTS, payload=payload)

    def move_agent_to_site(self, site_id: str, cpt_name: str) -> "DataType":
        """
        Move an agent that matches the filter to a specified site based on its ID.

        Possible response messages
        200 - Success
        400 - Invalid user input received. See error details for further information
        401 - Unauthorized access - please sign in and retry
        403 - User has insufficient permissions to perform the requested action

        Args:
            site_id (str) : The site to move the agent on
            cpt_name (str): The computer to move

        Returns:
            DataType: response data
        """

        payload = {"data": {"targetSiteId": site_id}, "filter": {"computerName__like": cpt_name}}
        return self.fetch(endpoint=S1Endpoint.AGENTS_ACTIONS_MOVE_TO_SITE, payload=payload)

    # ****************************************************************
    # Methods: Users

    def login_by_api_token(self) -> "DataType":
        """
        Log in to the API with an API token.

        Possible response messages
        200 - user logged in
        400 - Invalid user input received. See error details for further information.
        401 - User authentication failed

        Returns:
            DataType: data with user token and user name
        """

        payload = {"data": {"apiToken": self._api_token}}
        return self.fetch(endpoint=S1Endpoint.USERS_LOGIN_BY_API_TOKEN, payload=payload)

    def logout(self, payload: dict[str, Any] | None = None) -> "DataType":
        """
        Log out the authenticated user.

        Possible response messages:
        200 - User logged out successfully.
        401 - Unauthorized access - please sign in and retry.

        Args:
            payload (dict[str, Any]): Payload to send to the endpoint

        Returns:
            DataType: Logout response data
        """

        return self.fetch(S1Endpoint.USERS_LOGOUT, payload or {})

    # ****************************************************************
    # Methods: Applications

    def applications(
        self,
        vendors: "StrType | None" = None,
        site_ids: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Get applications installed on endpoints.

        Possible response messages
        200 - Success
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry.
        403 - Insufficient permissions

        Args:
            vendors (str | list[str] | None) : List of vendors to include. If None, all are included
            site_ids (str | list[str] | None): List of site ids to filter
            payload (dict[str, Any] | None)  : Payload to send to the endpoint

        Returns:
            DataType: Applications data based on the provided filters
        """

        if payload is None:
            payload = {}

        if vendors is not None:
            payload["vendors"] = self._unify_str_list(vendors)

        if site_ids is not None:
            payload["siteIds"] = self._unify_str_list(site_ids)

        return self.fetch(S1Endpoint.APPLICATIONS_INVENTORY, payload)

    def applications_with_risks(
        self,
        vendors: "StrType | None" = None,
        site_ids: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Get applications with known CVEs.

        Possible response messages
        200 - Success
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry.
        403 - Insufficient permissions

        Args:
            vendors (str | list[str] | None) : List of vendors to include. If None, all are included
            site_ids (str | list[str] | None): List of site ids to filter
            payload (dict[str, Any] | None)  : Payload to send to the endpoint

        Returns:
            DataType: Applications data based on the provided filters
        """

        if payload is None:
            payload = {}

        if vendors is not None:
            payload["vendors"] = self._unify_str_list(vendors)

        if site_ids is not None:
            payload["siteIds"] = self._unify_str_list(site_ids)

        return self.fetch(S1Endpoint.APPLICATIONS_WITH_RISKS, payload)

    def cves(
        self, site_ids: "StrType | None" = None, payload: dict[str, Any] | None = None
    ) -> "DataType":
        """
        Get known CVEs for applications installed on endpoints with 'Application Risk-enabled Agents'.

        Possible response messages
        200 - Success
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry.
        403 - Insufficient permissions

        Args:
            site_ids (str | list[str] | None): List of site ids to filter
            payload (dict[str, Any])         : Payload to send to the endpoint

        Returns:
            DataType: CVEs data based on the provided filters
        """

        if payload is None:
            payload = {}

        if site_ids is not None:
            payload["siteIds"] = self._unify_str_list(site_ids)

        return self.fetch(S1Endpoint.APPLICATIONS_CVES, payload)

    def application_cves(
        self,
        application_ids: "StrType | None" = None,
        application_name: str | None = None,
        application_vendor: str | None = None,
        site_ids: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Get CVEs for a specific appliation.

        Possible response messages
        200 - Success
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry.
        403 - Insufficient permissions

        Args:
            application_ids (str | list[str] | None): List of applications to include
            application_name (str | None)           : Application name, if application ids are not specified
            application_vendor (str | None)         : Application vendor, if application ids are not specified
            site_ids (str | list[str] | None)       : List of site ids to filter
            payload (dict[str, Any])                : Payload to send to the endpoint

        Returns:
            DataType: CVEs data based on the provided filters
        """

        if payload is None:
            payload = {}

        if application_ids is not None:
            payload["applicationIds"] = self._unify_str_list(application_ids)

        elif application_name is not None and application_vendor is not None:
            payload["applicationName"] = application_name
            payload["applicationVendor"] = application_vendor

        else:
            raise ValueError(
                f"{Context()}::You must provide either application IDs or specify an application name and vendor"
            )

        if site_ids is not None:
            payload["siteIds"] = self._unify_str_list(site_ids)

        return self.fetch(S1Endpoint.APPLICATIONS_APP_CVES, payload)

    # ****************************************************************
    # Methods: Groups

    def groups(self, site_id: str | None, payload: dict[str, Any] | None = None) -> "DataType":
        """
        Get data of groups that match the filter.

        Possible response messages:
        200 - Success
        400 - Invalid user input received. See error details for further information
        401 - Unauthorized access - please sign in and retry

        Args:
            site_id (str)           : The site to remove groups from
            payload (dict[str, Any]): Payload to send to the endpoint

        Returns:
            DataType: Groups data based on the provided filters
        """

        if payload is None:
            payload = {}

        payload = {"filter": {"siteId": site_id}}
        return self.fetch(S1Endpoint.GROUPS, payload)

    def move_agent_to_group(
        self, group_id: str, cpt_name: str | None = None, cpt_ids: "StrType | None" = None
    ) -> "DataType":
        """
        Move an Agent that matches the filter to a specified group in the same site.

        Can either supply computerName or a list of IDs.

        Possible response messages:
        204 - Success
        400 - Invalid user input received. See error details for further information
        401 - Unauthorized access - please sign in and retry
        403 - Insufficient permissions
        409 - Conflict

        Args:
            group_id (str)                  : The ID of th group the agent must be moved in
            cpt_name (str | None)           : The name of the computer whose agent will be moved
            cpt_ids (str | list[str] | None): A list of IDs of computer whose agent will be moved

        Returns:
            DataType: Response data
        """

        if cpt_ids is not None:
            payload = {"filter": {"ids": self._unify_str_list(cpt_ids)}}

        elif cpt_name is not None:
            payload = {"filter": {"computerName__like": cpt_name}}

        else:
            raise ValueError(
                f"{Context()}.move_agent_to_group::Neither computer_name nor cpt_ids specified"
            )

        return self.fetch(
            S1Endpoint.GROUPS_MOVE_AGENTS, payload=payload, path_fmt={"groupId": group_id}
        )

    # ****************************************************************
    # Methods: Sites

    def sites_by_id(self, site_id: str, payload: dict[str, Any] | None = None) -> "DataType":
        """
        Get the data of the Site matchin the provided ID. To get the ID, run "sites".

        The response shows the Site expiration date, SKU, licenses (total and active), token, Account name and ID, who and when it was created and changed, and its status.

        Possible response messages:
        200 - Success
        401 - Unauthorized access - please sign in and retry.
        404 - Site not found

        Args:
            site_id (str)           : The ID of the site data will be retrieved
            payload (dict[str, Any]): Payload to send to the endpoint

        Returns:
            DataType: Data of the site matching the provided ID
        """

        return self.fetch(
            S1Endpoint.SITES_BY_ID, payload=payload or {}, path_fmt={"siteId": site_id}
        )

    def sites(self, payload: dict[str, Any] | None = None) -> "DataType":
        """
        Retrieve the sites that match the provided filters.

        The response includes the IDs of Sites, which you can use in other commands.

        Possible response messages:
        200 - Success
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry.

        Args:
            payload (dict[str, Any]): Payload to send to the endpoint

        Returns:
            DataType: Data of the site matching the provided ID
        """

        return self.fetch(S1Endpoint.SITES, payload=payload or {})

    def threats(
        self,
        incident_statuses: "StrType | None" = None,
        incident_statuses_nin: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Get data of threats that match the filter.

        Possible response messages:
        200 - Success
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry.

        Args:
            incident_statuses (str | list[str] | None)    : Filter threats with specific incident statuses
            incident_statuses_nin (str | list[str] | None): Exclude threats with specific incident statuses
            payload (dict[str, Any])                      : Payload to send to the endpoint

        Returns:
            DataType: Threats data based on the provided filters
        """

        if payload is None:
            payload = {}

        if incident_statuses is not None:
            payload["incidentStatuses"] = self._unify_str_list(incident_statuses)

        if incident_statuses_nin is not None:
            payload["incidentStatusesNin"] = self._unify_str_list(incident_statuses_nin)

        return self.fetch(S1Endpoint.THREATS, payload)
