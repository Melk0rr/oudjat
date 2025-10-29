"""
A module that handles SentinelOne API connection and interactions.
"""

import re
from typing import Any, override
from urllib.parse import urlparse

import requests

from oudjat.connectors.edr.sentinelone.s1_endpoints import S1Endpoint
from oudjat.utils.color_print import ColorPrint
from oudjat.utils.types import DataType, StrType

from ... import Connector


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
        password: str | None = None,
        api_token: str | None = None,
        port: int = 443,
    ) -> None:
        """
        Create a new instance of S1Connector.

        Args:
            target (str)   : SentinelOne URL
            username (str) : Username to use for the connection
            password (str) : Password to use for the connection
            api_token (str): API token. Replace the password if provided.
            port (int)     : Port number used for the connection
        """

        scheme = "http"
        if port == 443:
            scheme += "s"

        # Inject protocol if not found
        if not re.match(r"http(s?):", target):
            target = f"{scheme}://{target}"

        self._api_token: str | None = api_token
        super().__init__(
            target=urlparse(target), username=username, password=(self._api_token or password)
        )

        self._connection: requests.Session | None = None
        self._DEFAULT_HEADERS: dict[str, str] = {"Content-Type": "application/json"}

    # ****************************************************************
    # Methods

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

        if isinstance(str_list, list):
            str_list = ",".join(str_list)

        return str_list

    @override
    def connect(self) -> None:
        """
        Connect to the target.
        """

        if not self._connection:
            if self._api_token:
                ColorPrint.blue(f"Connecting to {self._target} with user API token")

                try:
                    data = self.login_by_api_token()
                    self._connection = data[0]["token"]

                # TODO: Better handle exception type
                except Exception as e:
                    raise e

        else:
            ColorPrint.blue(f"Connection to {self._target} is already initialized.")

    @override
    def fetch(
        self,
        endpoint: "S1Endpoint",
        payload: dict[str, Any],
        attributes: list[str] | None = None,
        path_fmt: dict[str, str] | None = None,
    ) -> DataType:
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

        res = []
        next_cursor = None

        endpoint_path = endpoint.path
        if path_fmt:
            endpoint_path = endpoint_path.format(**path_fmt)

        while True:
            if next_cursor:
                payload["cursor"] = next_cursor

            r_params = {
                "url": f"{self._target}{endpoint_path}",
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

            if req.status_code != 200:
                raise Exception(
                    f"{__class__.__name__}.fetch::An error occured while fetching data from {endpoint}\n{req_json['errors']}"
                )

            next_cursor = req_json.get("pagination", {}).get("nextCursor", None)
            if not next_cursor:
                break

        return res

    # ****************************************************************
    # Methods: Agents

    def agents(
        self,
        site_ids: StrType | None = None,
        payload: dict[str, Any] | None = None,
        infected: bool = False,
        net_statuses: StrType | None = None,
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

    def move_agent_to_site(self, site_id: str, cpt_name: str) -> DataType:
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

    def login_by_api_token(self) -> DataType:
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

    def logout(self, payload: dict[str, Any] | None = None) -> DataType:
        """
        Log out the authenticated user.

        Possible response messages:
        200 - User logged out successfully.
        401 - Unauthorized access - please sign in and retry.

        Args:
            payload (dict[str, Any])         : Payload to send to the endpoint

        Returns:
            DataType: Logout response data
        """

        return self.fetch(S1Endpoint.USERS_LOGOUT, payload or {})

    # ****************************************************************
    # Methods: Applications

    def cves(
        self, site_ids: StrType | None = None, payload: dict[str, Any] | None = None
    ) -> DataType:
        """
        Get known CVEs for applications installed on endpoints with 'Application Risk-enabled Agents'.

        Possible response messages
        200 - Success
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry.

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

    # ****************************************************************
    # Methods: Groups

    def groups(self, site_id: str | None, payload: dict[str, Any] | None = None) -> DataType:
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
        self, group_id: str, cpt_name: str | None = None, cpt_ids: StrType | None = None
    ) -> DataType:
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
                f"{__class__.__name__}.move_agent_to_group::Neither computer_name nor cpt_ids specified"
            )

        return self.fetch(
            S1Endpoint.GROUPS_MOVE_AGENTS, payload=payload, path_fmt={"groupId": group_id}
        )

    # ****************************************************************
    # Methods: Sites

    def sites_by_id(self, site_id: str, payload: dict[str, Any] | None = None) -> DataType:
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

    def sites(self, payload: dict[str, Any] | None = None) -> DataType:
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
        incident_statuses: StrType | None = None,
        incident_statuses_nin: StrType | None = None,
        payload: dict[str, Any] | None = None,
    ) -> DataType:
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
