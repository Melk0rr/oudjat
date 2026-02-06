"""
A module that handles Security Score Card API connections and interactions.
"""

import logging
import re
from typing import Any, override
from urllib.parse import ParseResult, urlparse

from oudjat.connectors.connector_methods import ConnectorMethod
from oudjat.connectors.ssc.exceptions import SSCAPIConnectionError
from oudjat.connectors.ssc.ssc_endpoints import SSCEndpoint
from oudjat.utils import DataType
from oudjat.utils.context import Context

from ..connector import Connector


class SSCConnector(Connector):
    """
    A class that handles Security Score Card API connections and interactions.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self,
        domain: str | list[str],
        username: str | None = None,
        api_token: str | None = None,
        port: int = 443,
    ) -> None:
        """
        Create a new instance of SSCConnector.

        Args:
            target (str)   : Security Score Card URL
            username (str) : Username to use for the connection
            api_token (str): API token. Stored as the connector credentials.password
            port (int)     : Port number used for the connection
        """

        self.logger: "logging.Logger" = logging.getLogger(__name__)

        scheme = "http"
        if port == 443:
            scheme += "s"

        _target = "https://api.securityscorecard.io/companies/"

        # Inject protocol if not found
        if not re.match(r"http(s?):", _target):
            _target = f"{scheme}://{_target}"

        self._target: "ParseResult"
        super().__init__(target=urlparse(_target), username=username, password=api_token)

        self._domains: list[str] = []
        if not isinstance(domain, list):
            domain = [domain]

        self._domains.extend(domain)

        self._DEFAULT_HEADERS: dict[str, str] = {
            "accept": "application/json",
            "content-type": "application/json",
        }

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
        if self._api_token:
            headers["Authorization"] = f"Token {self._api_token}"

        return headers

    def _request_params(
        self, payload: dict[str, Any], method: "ConnectorMethod", endpoint_path: str
    ) -> dict[str, Any]:
        """
        Return request parameters dictionary based on the provided payload, method and formatted path.

        Args:
            payload (dict[str, Any]): Request payload
            method (ConnectorMethod): Request method used for an endpoint connection
            endpoint_path (str)     : Final endpoint path

        Returns:
            dict[str, Any]: Final parameters
        """

        r_params = {
            "url": f"{self._target.geturl()}{endpoint_path}",
            "headers": self._headers,
            "json": payload,
        }

        if method is ConnectorMethod.GET:
            r_params["params"] = r_params.pop("json")

        return r_params

    @override
    def connect(self) -> None:
        """
        Connect to Security Score Card API using connector parameters.
        """

        pass

    @override
    def fetch(
        self,
        endpoint: "SSCEndpoint",
        domain: str,
        payload: dict[str, Any],
        attributes: list[str] | None = None,
        path_fmt: dict[str, str] | None = None,
    ) -> "DataType":

        context = Context()

        res = []

        endpoint_path = f"{domain}{endpoint.path}"
        if path_fmt:
            endpoint_path = endpoint_path.format(**path_fmt)

        self.logger.debug(f"{context}::{endpoint} > {payload}")

        r_params = self._request_params(payload, endpoint.method, endpoint_path)
        req = endpoint.method(**r_params)

        req_json = req.json()

        if "data" in req_json:
            if isinstance(req_json["data"], list):
                res.extend(req_json["data"])

            else:
                res.append(req_json["data"])

        self.logger.debug(f"{context}::{endpoint} > {req_json}")

        if req.status_code != 200:
            raise SSCAPIConnectionError(
                f"{context}::An error occured while fetching data from {endpoint}\n{req_json['errors']}"
            )

        return res


