"""
A module that handles SentinelOne API connection and interactions.
"""

import logging
import re
from typing import Any, TypeAlias, override
from urllib.parse import ParseResult, urlparse

import requests

from oudjat.utils import FileUtils
from oudjat.utils.context import Context
from oudjat.utils.credentials import NoCredentialsError
from oudjat.utils.types import DataType, StrType

from ... import Connector, ConnectorMethod
from .exceptions import SentinelOneAPIConnectionError, SentinelOneEndpointFormatError
from .s1_analyst_verdicts import S1AnalystVerdict
from .s1_endpoints import S1Endpoint
from .s1_incident_statuses import S1IncidentStatus
from .s1_mitigation_modes import S1MitigationMode

S1IncidentStatusType: TypeAlias = "str | S1IncidentStatus | list[str | S1IncidentStatus]"
S1AnalystVerdictType: TypeAlias = "str | S1AnalystVerdict | list[str | S1AnalystVerdict]"

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
    def fetch(
        self,
        endpoint: "S1Endpoint",
        payload: dict[str, Any],
        path_fmt: dict[str, str] | None = None,
    ) -> "DataType":
        """
        Perform a search query through the API to retrieve data based on provided endpoint and .

        Args:
            endpoint (S1Endpoints)          : SentinelOne endpoint the query payload will be send to
            payload (dict[str, Any] | None) : Payload to send to the provided endpoint
            path_fmt (dict[str, Any] | None): A dictionary of variable names that will be replaced in the endpoint path

        Returns:
            DataType: list of retrieved elements
        """

        context = Context()

        res = []
        next_cursor = None

        endpoint_path = endpoint.path

        if "{" and "}" in endpoint_path and path_fmt is None:
            raise SentinelOneEndpointFormatError(f"{context}::SentinelOne endpoint {endpoint} needs formatting")

        if path_fmt:
            endpoint_path = endpoint_path.format(**path_fmt)

        self.logger.debug(f"{context}::{endpoint} > {payload}")
        while True:
            if next_cursor:
                payload["cursor"] = next_cursor

            r_params = self._request_params(payload, endpoint.method, endpoint_path)
            req = endpoint.method(**r_params)
            req_json = req.json()

            self.logger.debug(f"{context}::{endpoint} > {req_json}")

            if "data" in req_json:
                if isinstance(req_json["data"], list):
                    res.extend(req_json["data"])

                else:
                    res.append(req_json["data"])

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
        limit: int = 1000,
        payload: dict[str, Any] | None = None,
        infected: bool = False,
    ) -> "DataType":
        """
        Return the agents based on the provided filter.

        Possible response messages
        200 - Success
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry.

        Args:
            site_ids (str | list[str] | None): List of site ids to filter
            limit (int)                      : The number of agents per cursor call
            payload (dict[str, Any])         : Payload to send to the endpoint
            infected (bool)                  : Whether to only include agents with at least one active threat

        Returns:
            DataType: response data with agentID
        """

        if payload is None:
            payload = {}

        payload["limit"] = limit

        if "skipCount" not in payload:
            payload["skipCount"] = True

        if site_ids is not None:
            payload["siteIds"] = self._unify_str_list(site_ids)

        if infected:
            payload["infected"] = True

        return self.fetch(endpoint=S1Endpoint.AGENTS, payload=payload)

    def agents_export(
        self,
        site_ids: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
        infected: bool = False,
    ) -> "DataType":
        """
        Return the agents based on the provided filter.

        Possible response messages
        200 - Success
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry.

        Args:
            site_ids (str | list[str] | None)    : List of site ids to filter
            limit (int)                          : The number of agents per cursor call
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

        endpoint = S1Endpoint.AGENTS_EXPORT
        req = endpoint.method(**self._request_params(payload, endpoint.method, endpoint.path))

        if req.status_code != 200:
            raise SentinelOneAPIConnectionError(
                f"{Context()}::An error occured while fetching data from {endpoint}"
            )

        return FileUtils.parse_csv_str(req.content.decode().replace('"', ""), delimiter=",")

    def move_agent_to_site(self, site_id: str, agent_name: "StrType") -> "DataType":
        """
        Move an agent that matches the filter to a specified site based on its ID.

        Possible response messages
        200 - Success
        400 - Invalid user input received. See error details for further information
        401 - Unauthorized access - please sign in and retry
        403 - User has insufficient permissions to perform the requested action

        Args:
            site_id (str)   : The site to move the agent on
            agent_name (str): The agents to move

        Returns:
            DataType: response data
        """

        if not isinstance(agent_name, list):
            agent_name = [agent_name]

        data = []
        for name in agent_name:
            payload = {
                "data": {"targetSiteId": site_id},
                "filter": {"computerName__like": name},
            }

            data.extend(
                self.fetch(endpoint=S1Endpoint.AGENTS_ACTIONS_MOVE_TO_SITE, payload=payload)
            )

        return data

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
    # Methods: Alerts

    def _unify_status(self, s: "str | S1IncidentStatus") -> str:
        """
        Unify incident status type into a valid string.

        Args:
            s (str | S1IncidentStatus): Incident status to unify

        Returns:
            str: A valid S1 incident status string value
        """

        return str(s) if isinstance(s, S1IncidentStatus) else str(S1IncidentStatus[s.upper()])

    def _unify_verdict(self, v: "str | S1AnalystVerdict") -> str:
        """
        Unify incident analyst verdict type into a valid string.

        Args:
            v (str | S1AnalystVerdict): Incident analyst verdict to unify

        Returns:
            str: A valid S1 incident analyst verdict string value
        """

        return str(v) if isinstance(v, S1AnalystVerdict) else str(S1AnalystVerdict[v.upper()])

    def _update_filter_status(
        self,
        incident_filter: dict[str, Any],
        status: "S1IncidentStatusType | None",
        exclude: bool = True,
    ) -> None:
        """
        Unify an incident status value into a valid status string.

        Args:
            incident_filter (dict[str, Any])                                     : The incident filter to update if a status is provided
            status (S1IncidentStatusType | None): Status to filter
            exclude (bool)                                                       : If true, the provided status will be excluded from the search.
        """

        if status is not None:
            if not isinstance(status, list):
                status = [status]

            status = list(set(map(self._unify_status, status)))

            if len(status) > 0:
                mode = "incidentStatusesNin" if exclude else "incidentStatuses"
                incident_filter[mode] = status

    def _update_filter_verdict(
        self,
        incident_filter: dict[str, Any],
        verdict: "S1AnalystVerdictType | None",
        exclude: bool = True,
    ) -> None:
        """
        Unify an incident status value into a valid status string.

        Args:
            incident_filter (dict[str, Any])                                      : The incident filter to update if a status is provided
            verdict (str | S1AnalystVerdict | list[str | S1AnalystVerdict] | None): Status to filter
            exclude (bool)                                                        : If true, the provided status will be excluded from the search.
        """

        if verdict is not None:
            if not isinstance(verdict, list):
                verdict = [verdict]

            verdict = list(set(map(self._unify_verdict, verdict)))

            if len(verdict) > 0:
                mode = "analystVerdictsNin" if exclude else "analystVerdicts"
                incident_filter[mode] = verdict

    def alert_verdict(
        self,
        verdict: "str | S1AnalystVerdict",
        alert_ids: "StrType | None" = None,
        site_ids: "StrType | None" = None,
        status_filter: "S1IncidentStatusType | None" = S1IncidentStatus.UNRESOLVED,
        verdict_filter: "S1AnalystVerdictType | None" = S1AnalystVerdict.UNDEFINED,
        process_path: "StrType | None" = None,
        alert_filter: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Change the verdict of an alert.

        Response Messages
        200 - Threats incident successfully updated
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry

        Args:
            verdict (str | S1AnalystVerdict)            : The verdict to assign to the filtered alerts
            alert_ids (str | list[str] | None)          : Ids of the alert to change verdict of
            site_ids (str | list[str] | None)           : Site ids of the alerts
            status_filter (S1IncidentStatusType | None) : Treat only the alerts with the provided status. Default UNRESOLVED
            verdict_filter (S1AnalystVerdictType | None): Treat only the alerts with the provided verdict. Default UNDEFINED
            process_path (str | list[str] | None)       : Path of the process which triggered the alert
            alert_filter (dict[str, Any])               : A dictionary of alert filters

        Returns:
            DataType: Response containing the number of affected verdicts and eventual errors
        """

        if alert_filter is None:
            alert_filter = {}

        if alert_ids is not None:
            if not isinstance(alert_ids, list):
                alert_ids = [alert_ids]

            alert_filter["ids"] = self._unify_str_list(alert_ids)

        if site_ids is not None:
            alert_filter["siteIds"] = self._unify_str_list(site_ids)

        # Set status filter
        self._update_filter_status(alert_filter, status_filter)

        # Set verdict filter
        self._update_filter_verdict(alert_filter, verdict_filter)

        if process_path is not None:
            alert_filter["sourceProcessFilePath__contains"] = self._unify_str_list(process_path)

        if not isinstance(verdict, S1AnalystVerdict):
            verdict = S1AnalystVerdict[verdict.upper()]

        data = {"analystVerdict": str(verdict)}

        return self.fetch(S1Endpoint.ALERTS_ANALYST_VERDICT, {"filter": alert_filter, "data": data})

    def alert_incident(
        self,
        status: "str | S1IncidentStatus",
        alert_ids: "StrType | None" = None,
        site_ids: "StrType | None" = None,
        status_filter: "S1IncidentStatusType | None" = S1IncidentStatus.UNRESOLVED,
        verdict_filter: "S1AnalystVerdictType | None" = S1AnalystVerdict.UNDEFINED,
        process_path: "StrType | None" = None,
        alert_filter: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Change the verdict of an alert.

        Response Messages
        200 - Threats incident successfully updated
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry

        Args:
            status (str | S1IncidentStatus)             : The verdict to assign to the filtered alerts
            alert_ids (str | list[str] | None)          : Ids of the alert to change verdict of
            site_ids (str | list[str] | None)           : Site ids of the alerts
            status_filter (S1IncidentStatusType | None) : Treat only the alerts with the provided status. Default UNRESOLVED
            verdict_filter (S1AnalystVerdictType | None): Treat only the alerts with the provided verdict. Default UNDEFINED
            process_path (str | list[str] | None)       : Path of the process which triggered the alert
            alert_filter (dict[str, Any])               : A dictionary of alert filters

        Returns:
            DataType: Response containing the number of affected verdicts and eventual errors
        """

        if alert_filter is None:
            alert_filter = {}

        if alert_ids is not None:
            if not isinstance(alert_ids, list):
                alert_ids = [alert_ids]

            alert_filter["ids"] = self._unify_str_list(alert_ids)

        if site_ids is not None:
            alert_filter["siteIds"] = self._unify_str_list(site_ids)

        # Set status filter
        self._update_filter_status(alert_filter, status_filter)

        # Set verdict filter
        self._update_filter_verdict(alert_filter, verdict_filter)

        if process_path is not None:
            alert_filter["sourceProcessFilePath__contains"] = self._unify_str_list(process_path)

        if not isinstance(status, S1IncidentStatus):
            status = S1IncidentStatus[status.upper()]

        data = {"incidentStatus": str(status)}

        return self.fetch(S1Endpoint.ALERTS_INCIDENT, {"filter": alert_filter, "data": data})

    # ****************************************************************
    # Methods: Threats

    def threats(
        self,
        status_filter: "S1IncidentStatusType | None" = S1IncidentStatus.UNRESOLVED,
        verdict_filter: "S1AnalystVerdictType | None" = S1AnalystVerdict.UNDEFINED,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Get data of threats that match the filter.

        Possible response messages:
        200 - Success
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry.

        Args:
            status_filter (S1IncidentStatusType | None) : Treat only the alerts with the provided status. Default UNRESOLVED
            verdict_filter (S1AnalystVerdictType | None): Treat only the alerts with the provided verdict. Default UNDEFINED
            loop (bool)                                 : If true, will loop until there is no results left
            payload (dict[str, Any])                    : Payload to send to the endpoint

        Returns:
            DataType: Threats data based on the provided filters
        """

        if payload is None:
            payload = {}

        self._update_filter_status(payload, status_filter)
        self._update_filter_verdict(payload, verdict_filter)

        return self.fetch(S1Endpoint.THREATS, payload)

    def threat_verdict(
        self,
        verdict: "str | S1AnalystVerdict",
        alert_ids: "StrType | None" = None,
        site_ids: "StrType | None" = None,
        status_filter: "S1IncidentStatusType | None" = S1IncidentStatus.UNRESOLVED,
        verdict_filter: "S1AnalystVerdictType | None" = S1AnalystVerdict.UNDEFINED,
        file_path: "StrType | None" = None,
        alert_filter: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Change the verdict of a threat.

        Response Messages
        200 - Threats incident successfully updated
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry

        Args:
            verdict (str | S1AnalystVerdict)            : The verdict to assign to the filtered threats
            alert_ids (str | list[str] | None)          : Ids of the threat to change verdict of
            site_ids (str | list[str] | None)           : Site ids of the threats
            status_filter (S1IncidentStatusType | None) : Treat only the alerts with the provided status. Default UNRESOLVED
            verdict_filter (S1AnalystVerdictType | None): Treat only the alerts with the provided verdict. Default UNDEFINED
            file_path (str | list[str] | None)          : Path of the process which triggered the threat
            alert_filter (dict[str, Any])               : A dictionary of threat filters

        Returns:
            DataType: Response containing the number of affected verdicts and eventual errors
        """

        if alert_filter is None:
            alert_filter = {}

        if alert_ids is not None:
            if not isinstance(alert_ids, list):
                alert_ids = [alert_ids]

            alert_filter["ids"] = self._unify_str_list(alert_ids)

        if site_ids is not None:
            alert_filter["siteIds"] = self._unify_str_list(site_ids)

        # Set status filter
        self._update_filter_status(alert_filter, status_filter)

        # Set verdict filter
        self._update_filter_verdict(alert_filter, verdict_filter)

        if file_path is not None:
            alert_filter["filePath__contains"] = self._unify_str_list(file_path)

        if not isinstance(verdict, S1AnalystVerdict):
            verdict = S1AnalystVerdict[verdict.upper()]

        data = {"analystVerdict": str(verdict)}

        return self.fetch(
            S1Endpoint.THREATS_ANALYST_VERDICT, {"filter": alert_filter, "data": data}
        )

    def threat_incident(
        self,
        status: "str | S1IncidentStatus",
        verdict: "str | S1AnalystVerdict",
        threat_ids: "StrType | None" = None,
        site_ids: "StrType | None" = None,
        status_filter: "S1IncidentStatusType | None" = S1IncidentStatus.UNRESOLVED,
        verdict_filter: "S1AnalystVerdictType | None" = S1AnalystVerdict.UNDEFINED,
        file_path: "StrType | None" = None,
        loop: bool = False,
        alert_filter: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Change the verdict and status of a threat.

        Response Messages
        200 - Threats incident successfully updated
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry

        Args:
            status (str | S1IncidentStatus)             : The verdict to assign to the filtered threats
            verdict (str | S1AnalystVerdict)            : The verdict to assign to the filtered threats
            threat_ids (str | list[str] | None)         : Ids of the alert to change verdict of
            site_ids (str | list[str] | None)           : Site ids of the alerts
            status_filter (S1IncidentStatusType | None) : Treat only the alerts with the provided status. Default UNRESOLVED
            verdict_filter (S1AnalystVerdictType | None): Treat only the alerts with the provided verdict. Default UNDEFINED
            file_path (str | list[str] | None)          : Path of the process which triggered the alert
            loop (bool)                                 : If true, loop until there is no threat to process
            alert_filter (dict[str, Any])               : A dictionary of alert filters

        Returns:
            DataType: Response containing the number of affected verdicts and eventual errors
        """

        if alert_filter is None:
            alert_filter = {}

        if threat_ids is not None:
            if not isinstance(threat_ids, list):
                threat_ids = [threat_ids]

            alert_filter["ids"] = self._unify_str_list(threat_ids)

        if site_ids is not None:
            alert_filter["siteIds"] = self._unify_str_list(site_ids)

        # Set status filter
        self._update_filter_status(alert_filter, status_filter)

        # Set verdict filter
        self._update_filter_verdict(alert_filter, verdict_filter)

        if file_path is not None:
            alert_filter["filePath__contains"] = self._unify_str_list(file_path)

        if not isinstance(status, S1IncidentStatus):
            status = S1IncidentStatus[status.upper()]

        if not isinstance(verdict, S1AnalystVerdict):
            verdict = S1AnalystVerdict[verdict.upper()]

        input_data = {"incidentStatus": str(status), "analystVerdict": str(verdict)}

        res = []
        if loop:
            while True:
                q = self.fetch(
                    S1Endpoint.THREATS_INCIDENT, {"filter": alert_filter, "data": input_data}
                )

                if q[0]["affected"] == 0:
                    break

                res.extend(q)

        else:
            res.extend(
                self.fetch(
                    S1Endpoint.THREATS_INCIDENT, {"filter": alert_filter, "data": input_data}
                )
            )

        return res

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

    def groups(self, site_ids: "StrType | None", payload: dict[str, Any] | None = None) -> "DataType":
        """
        Get data of groups that match the filter.

        Possible response messages:
        200 - Success
        400 - Invalid user input received. See error details for further information
        401 - Unauthorized access - please sign in and retry

        Args:
            site_ids (str)           : The site to remove groups from
            payload (dict[str, Any]) : Payload to send to the endpoint

        Returns:
            DataType: Groups data based on the provided filters
        """

        if payload is None:
            payload = {}

        if site_ids is not None:
            if not isinstance(site_ids, list):
                site_ids = [site_ids]

            payload["siteIds"] = site_ids


        return self.fetch(S1Endpoint.GROUPS, payload)

    def group_policy_update(
        self,
        group_id: "StrType",
        malicious_mitigation: "S1MitigationMode | None" = None,
        suspicious_mitigation: "S1MitigationMode | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Update the provided groups (by id) policy.

        Args:
            group_id (str | list[str])                     : Group to update the policy of
            malicious_mitigation (S1MitigationMode | None) : Malicious policy to set
            suspicious_mitigation (S1MitigationMode | None): Suspicious policy to set
            payload (dict[str, Any])                       : Payload to send

        Returns:
            DataType: Update result
        """

        if not isinstance(group_id, list):
            group_id = [group_id]

        if payload is None:
            payload = {}
            payload["data"] = {}

        if malicious_mitigation is not None:
            payload["data"]["mitigationMode"] = str(malicious_mitigation)

        if suspicious_mitigation is not None:
            payload["data"]["mitigationModeSuspicious"] = str(suspicious_mitigation)

        res = []
        for gid in group_id:
            res.extend(
                self.fetch(S1Endpoint.GROUPS_POLICY_UPDATE, payload, path_fmt={"groupId": gid})
            )

        return res

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

        req = self.fetch(S1Endpoint.SITES, payload=payload or {})
        return next(iter(req))["sites"]

    def sites_by_name(self, names: "StrType", payload: dict[str, Any] | None = None) -> "DataType":
        """
        Retrieve sites based on the provided name list.

        The response includes the IDs of Sites, which you can use in other commands.

        Possible response messages:
        200 - Success
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry.

        Args:
            names (list[str])       : A list of site names to retrieve
            payload (dict[str, Any]): Payload to send to the endpoint

        Returns:
            DataType: Data of the site matching the provided ID
        """

        if not isinstance(names, list):
            names = [names]

        def filter_by_name(site: dict[str, Any]) -> bool:
            return site["name"] in names

        return list(filter(filter_by_name, self.sites(payload)))
