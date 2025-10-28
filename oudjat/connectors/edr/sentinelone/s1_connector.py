"""
A module that handles SentinelOne API connection and interactions.
"""

import re
from typing import Any, override
from urllib.parse import urlparse

import requests

from oudjat.connectors.edr.sentinelone.s1_endpoints import S1Endpoint
from oudjat.utils.color_print import ColorPrint
from oudjat.utils.types import StrType

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

    def _unify_str_list_args(self, str_list: StrType) -> str:
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
    ) -> list[dict[str, Any]]:
        """
        Perform a search query through the API to retrieve data based on provided endpoint and .

        Args:
            endpoint (S1Endpoints)         : SentinelOne endpoint the query payload will be send to
            attributes (list[str] | None)  : List of attributes to keep per elements
            payload (dict[str, Any] | None): Payload to send to the provided endpoint

        Returns:
            list[dict[str, Any]]: list of retrieved elements
        """

        res = []
        next_cursor = None
        while True:
            if next_cursor:
                payload["cursor"] = next_cursor

            r_params = {
                "url": f"{self._target}{endpoint.path}",
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
        net_statuses: StrType | None = None
    ) -> list[dict[str, Any]]:
        """
        Return the agents based on the provided filter.

        Possible response messages
        200 - Success
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry.

        Args:
            site_ids (str | list[str] | None)    : List of site ids to filter
            payload (dict[str, Any])             : Payload to send to the endpoint
            infected (bool)                      : Whether to include only agents with at least one active threat
            net_statuses (str | list[str] | None): Network statuses to filter

        Returns:
            list[dict[str, Any]]: data with agentID
        """

        if payload is None:
            payload = {}

        if site_ids is not None:
            payload["siteIds"] = self._unify_str_list_args(site_ids)

        if infected:
            payload["infected"] = True

        if net_statuses is not None:
            payload["netStatuses"] = self._unify_str_list_args(net_statuses)

        return self.fetch(endpoint=S1Endpoint.AGENTS, payload=payload)

    # ****************************************************************
    # Methods: Users

    def login_by_api_token(self) -> list[dict[str, Any]]:
        """
        Log in to the API with an API token.

        Possible response messages
        200 - user logged in
        400 - Invalid user input received. See error details for further information.
        401 - User authentication failed

        Returns:
            list[dict[str, Any]]: data with user token and user name
        """

        payload = {"data": {"apiToken": self._api_token}}
        return self.fetch(endpoint=S1Endpoint.USERS_LOGIN_BY_API_TOKEN, payload=payload)
