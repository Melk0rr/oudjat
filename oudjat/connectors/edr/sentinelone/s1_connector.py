"""
A module that handles SentinelOne API connection and interactions.
"""

import logging
import re
from typing import Any, TypeAlias, override
from urllib.parse import ParseResult, urlparse

from yaspin import yaspin

from oudjat.control.vulnerability.severity import Severity
from oudjat.utils import Context, DataType, FileUtils, NoCredentialsError, StrType
from oudjat.utils.logging import spinner_log

from ... import Connector, ConnectorMethod
from .exceptions import SentinelOneAPIConnectionError, SentinelOneEndpointFormatError
from .s1_analyst_verdicts import S1AnalystVerdict
from .s1_endpoints import S1Endpoint
from .s1_incident_statuses import S1IncidentStatus
from .s1_incident_types import S1IncidentType
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

        self._connection: "str | None" = None
        self._DEFAULT_HEADERS: dict[str, str] = {"Content-Type": "application/json"}

    # ****************************************************************
    # Methods - helpers

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
            headers["Authorization"] = f"Bearer {self._connection}"

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
        statuses: "S1IncidentStatusType | None",
        incident_type: "S1IncidentType",
        exclude: bool = False,
    ) -> None:
        """
        Unify an incident status value into a valid status string.

        Args:
            incident_filter (dict[str, Any])      : The incident filter to update if a status is provided
            statuses (S1IncidentStatusType | None): Status to filter
            incident_type (S1IncidentType)        : The type of incident
            exclude (bool)                        : Whether to exclude the provided status
        """

        if statuses is not None:
            filter_props = {
                S1IncidentType.ALERT: {True: "incidentStatus", False: "incidentStatus"},
                S1IncidentType.THREAT: {True: "incidentStatusesNin", False: "incidentStatuses"},
            }

            if incident_type is S1IncidentType.ALERT:
                exclude = False

            if not isinstance(statuses, list):
                statuses = [statuses]

            unified_statuses = list(set(map(self._unify_status, statuses)))

            if len(unified_statuses) > 0:
                prop = filter_props[incident_type][exclude]
                incident_filter[prop] = self._unify_str_list(
                    unified_statuses
                    if incident_type is S1IncidentType.THREAT
                    else next(iter(unified_statuses))
                )

    def _update_filter_verdict(
        self,
        incident_filter: dict[str, Any],
        verdicts: "S1AnalystVerdictType | None",
        incident_type: "S1IncidentType",
        exclude: bool = False,
    ) -> None:
        """
        Unify an incident status value into a valid status string.

        Args:
            incident_filter (dict[str, Any])                                       : The incident filter to update if a status is provided
            verdicts (str | S1AnalystVerdict | list[str | S1AnalystVerdict] | None): Status to filter
            incident_type (S1IncidentType)                                         : The type of incident
            exclude (bool)                                                         : Whether to exclude the provided status
        """

        if verdicts is not None:
            filter_props = {
                S1IncidentType.ALERT: {True: "analystVerdict", False: "analystVerdict"},
                S1IncidentType.THREAT: {True: "analystVerdictsNin", False: "analystVerdicts"},
            }

            if incident_type is S1IncidentType.ALERT:
                exclude = False

            if not isinstance(verdicts, list):
                verdicts = [verdicts]

            unified_verdicts: list[str] = list(set(map(self._unify_verdict, verdicts)))

            if len(unified_verdicts) > 0:
                prop = filter_props[incident_type][exclude]
                incident_filter[prop] = self._unify_str_list(
                    unified_verdicts
                    if incident_type is S1IncidentType.THREAT
                    else next(iter(unified_verdicts))
                )

    # ****************************************************************
    # Methods - access

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

        if self._credentials is None:
            raise NoCredentialsError(f"{Context()}::No credentials provided")

        payload = {
            "data": {"apiToken": self._api_token},
        }
        return self.fetch(endpoint=S1Endpoint.USERS_LOGIN_BY_API_TOKEN, payload=payload)

    def login_by_token(self) -> "DataType":
        """
        Log in a user with an authentication token.

        Possible response messages
        200 - user logged in
        400 - Invalid user input received. See error details for further information.
        401 - User authentication failed

        Returns:
            DataType: data with user token and user name
        """

        if self._credentials is None:
            raise NoCredentialsError(f"{Context()}::No credentials provided")

        payload = {
            "data": {"token": self._api_token},
        }

        return self.fetch(endpoint=S1Endpoint.USERS_LOGIN_BY_TOKEN, payload=payload)

    def login(self) -> "DataType":
        """
        Log in a user by username/password.

        Possible response messages
        200 - user logged in
        400 - Invalid user input received. See error details for further information.
        401 - User authentication failed

        Returns:
            DataType: data with user token and user name
        """

        if self._credentials is None:
            raise NoCredentialsError(f"{Context()}::No credentials provided")

        payload = {
            "username": self._credentials.username,
            "password": self._credentials.password,
        }

        return self.fetch(endpoint=S1Endpoint.USERS_LOGIN, payload=payload)

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

    @override
    def connect(self) -> None:
        """
        Connect to the target.
        """

        context = Context()

        if self._credentials is None:
            raise NoCredentialsError(f"{context}::No credentials provided")

        if not self._connection:
            self.logger.info(f"Connecting to {self._target.netloc} with user API token")

            try:
                data = self.login_by_api_token()
                self._connection = data[0]["token"]

            except SentinelOneAPIConnectionError as e:
                if "Invalid operation" in str(e):
                    self.logger.warning("Failed to log in with API token. Passing user's password as header authorization...")
                    self._connection = self._credentials.password

                else:
                    raise SentinelOneAPIConnectionError(f"{context}::{e}")

            self.logger.info(f"Connected to {self._target.netloc}")

        else:
            self.logger.warning(f"Connection to {self._target.netloc} is already initialized.")

    # ****************************************************************
    # Methods - main

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

        next_cursor = None

        endpoint_path = endpoint.path

        if "{" and "}" in endpoint_path and path_fmt is None:
            raise SentinelOneEndpointFormatError(
                f"{context}::SentinelOne endpoint {endpoint} needs formatting"
            )

        if path_fmt:
            endpoint_path = endpoint_path.format(**path_fmt)

        self.logger.info(f"{endpoint} - {endpoint.description}")
        self.logger.debug(f"{context}::{payload}")

        res = []
        with yaspin(text=f"{endpoint.description}...") as spinner:
            try:
                while True:
                    if next_cursor:
                        payload["cursor"] = next_cursor

                    r_params = self._request_params(payload, endpoint.method, endpoint_path)
                    req = endpoint.method(**r_params)
                    req_json = req.json()

                    spinner_log(f"{context}::{endpoint} > {req_json}", self.logger.debug, spinner)

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

                spinner.ok(f"✅ Done running {endpoint} action")

            except Exception as e:
                spinner.fail(f"❌ Error while running {endpoint} action")
                raise e

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
        Retrieve agents based on the provided filter.

        Retrieve every agent details.

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
        Return a flat agent export.

        This endpoint is intended to do CSV exports.

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

        with yaspin(text=f"Exporting agents data using {endpoint}...") as spinner:
            req = endpoint.method(**self._request_params(payload, endpoint.method, endpoint.path))

            if req.status_code != 200:
                spinner.fail("❌ Error while exporting agents")
                raise SentinelOneAPIConnectionError(
                    f"{Context()}::An error occured while fetching data from {endpoint}"
                )

            spinner.ok("✅ Done exporting agents")

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
    # Methods: Alerts

    def alert_verdict(
        self,
        verdict: "str | S1AnalystVerdict",
        alert_ids: "StrType | None" = None,
        site_ids: "StrType | None" = None,
        status_filter: "S1IncidentStatusType | None" = None,
        verdict_filter: "S1AnalystVerdictType | None" = None,
        file_path: "StrType | None" = None,
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
            file_path (str | list[str] | None)          : Path of the process file which triggered the alert
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

        self._update_filter_status(alert_filter, status_filter, S1IncidentType.ALERT)
        self._update_filter_verdict(alert_filter, verdict_filter, S1IncidentType.ALERT)

        if file_path is not None:
            alert_filter["sourceProcessFilePath__contains"] = self._unify_str_list(file_path)

        if not isinstance(verdict, S1AnalystVerdict):
            verdict = S1AnalystVerdict[verdict.upper()]

        data = {"analystVerdict": str(verdict)}
        payload = {"filter": alert_filter, "data": data}

        return self.fetch(S1Endpoint.ALERTS_ANALYST_VERDICT, payload)

    def alert_incident(
        self,
        status: "str | S1IncidentStatus",
        alert_ids: "StrType | None" = None,
        site_ids: "StrType | None" = None,
        status_filter: "S1IncidentStatusType | None" = None,
        verdict_filter: "S1AnalystVerdictType | None" = None,
        file_path: "StrType | None" = None,
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
            file_path (str | list[str] | None)          : Path of the process file which triggered the alert
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

        self._update_filter_status(alert_filter, status_filter, S1IncidentType.ALERT)
        self._update_filter_verdict(alert_filter, verdict_filter, S1IncidentType.ALERT)

        if file_path is not None:
            alert_filter["sourceProcessFilePath__contains"] = self._unify_str_list(file_path)

        if not isinstance(status, S1IncidentStatus):
            status = S1IncidentStatus[status.upper()]

        data = {"incidentStatus": str(status)}
        payload = {"filter": alert_filter, "data": data}

        return self.fetch(S1Endpoint.ALERTS_INCIDENT, payload)

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

        self._update_filter_status(payload, status_filter, S1IncidentType.THREAT)
        self._update_filter_verdict(payload, verdict_filter, S1IncidentType.THREAT)

        return self.fetch(S1Endpoint.THREATS, payload)

    def threat_verdict(
        self,
        verdict: "str | S1AnalystVerdict",
        threat_ids: "StrType | None" = None,
        site_ids: "StrType | None" = None,
        status_filter: "S1IncidentStatusType | None" = S1IncidentStatus.UNRESOLVED,
        verdict_filter: "S1AnalystVerdictType | None" = S1AnalystVerdict.UNDEFINED,
        file_path: "StrType | None" = None,
        threat_filter: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Change the verdict of a threat.

        Response Messages
        200 - Threats incident successfully updated
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry

        Args:
            verdict (str | S1AnalystVerdict)            : The verdict to assign to the filtered threats
            threat_ids (str | list[str] | None)        : Ids of the threat to change verdict of
            site_ids (str | list[str] | None)           : Site ids of the threats
            status_filter (S1IncidentStatusType | None) : Treat only the alerts with the provided status. Default UNRESOLVED
            verdict_filter (S1AnalystVerdictType | None): Treat only the alerts with the provided verdict. Default UNDEFINED
            file_path (str | list[str] | None)          : Path of the process which triggered the threat
            threat_filter (dict[str, Any])              : A dictionary of threat filters

        Returns:
            DataType: Response containing the number of affected verdicts and eventual errors
        """

        if threat_filter is None:
            threat_filter = {}

        if threat_ids is not None:
            if not isinstance(threat_ids, list):
                threat_ids = [threat_ids]

            threat_filter["ids"] = self._unify_str_list(threat_ids)

        if site_ids is not None:
            threat_filter["siteIds"] = self._unify_str_list(site_ids)

        self._update_filter_status(threat_filter, status_filter, S1IncidentType.THREAT)
        self._update_filter_verdict(threat_filter, verdict_filter, S1IncidentType.THREAT)

        if "limit" not in threat_filter:
            threat_filter["limit"] = 1000

        if file_path is not None:
            threat_filter["filePath__contains"] = self._unify_str_list(file_path)

        if not isinstance(verdict, S1AnalystVerdict):
            verdict = S1AnalystVerdict[verdict.upper()]

        data = {"analystVerdict": str(verdict)}
        payload = {"filter": threat_filter, "data": data}

        return self.fetch(S1Endpoint.THREATS_ANALYST_VERDICT, payload)

    def threat_incident(
        self,
        status: "str | S1IncidentStatus",
        verdict: "str | S1AnalystVerdict",
        threat_ids: "StrType | None" = None,
        site_ids: "StrType | None" = None,
        status_filter: "S1IncidentStatusType | None" = S1IncidentStatus.UNRESOLVED,
        verdict_filter: "S1AnalystVerdictType | None" = S1AnalystVerdict.UNDEFINED,
        file_path: "StrType | None" = None,
        auto: bool = False,
        threat_filter: dict[str, Any] | None = None,
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
            auto (bool)                                 : If true, loop until there is no threat to process
            threat_filter (dict[str, Any])              : A dictionary of alert filters

        Returns:
            DataType: Response containing the number of affected verdicts and eventual errors
        """

        if threat_filter is None:
            threat_filter = {}

        if threat_ids is not None:
            if not isinstance(threat_ids, list):
                threat_ids = [threat_ids]

            threat_filter["ids"] = self._unify_str_list(threat_ids)

        if site_ids is not None:
            threat_filter["siteIds"] = self._unify_str_list(site_ids)

        self._update_filter_status(
            threat_filter,
            status_filter,
            S1IncidentType.THREAT,
        )
        self._update_filter_verdict(threat_filter, verdict_filter, S1IncidentType.THREAT)

        if "limit" not in threat_filter:
            threat_filter["limit"] = 1000

        if file_path is not None:
            threat_filter["filePath__contains"] = self._unify_str_list(file_path)

        if not isinstance(status, S1IncidentStatus):
            status = S1IncidentStatus[status.upper()]

        if not isinstance(verdict, S1AnalystVerdict):
            verdict = S1AnalystVerdict[verdict.upper()]

        input_data = {"incidentStatus": str(status), "analystVerdict": str(verdict)}
        payload = {"filter": threat_filter, "data": input_data}

        res = []
        if auto:
            while True:
                q = self.fetch(S1Endpoint.THREATS_INCIDENT, payload)

                if next(iter(q))["affected"] == 0:
                    break

                res.extend(q)

        else:
            res.extend(self.fetch(S1Endpoint.THREATS_INCIDENT, payload))

        return res

    # ****************************************************************
    # Methods: Applications

    def applications(
        self,
        names: "StrType | None" = None,
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
            names (str | list[str] | None)   : A list of application names
            vendors (str | list[str] | None) : List of vendors to include. If None, all are included
            site_ids (str | list[str] | None): List of site ids to filter
            payload (dict[str, Any] | None)  : Payload to send to the endpoint

        Returns:
            DataType: Applications data based on the provided filters
        """

        if payload is None:
            payload = {}

        if names is not None:
            payload["name__contains"] = self._unify_str_list(names)

        if vendors is not None:
            payload["vendor__contains"] = self._unify_str_list(vendors)

        if site_ids is not None:
            payload["siteIds"] = self._unify_str_list(site_ids)

        if "skipCount" not in payload:
            payload["skipCount"] = True

        if "limit" not in payload:
            payload["limit"] = 1000

        return self.fetch(S1Endpoint.APPLICATIONS_INVENTORY, payload)

    def applications_endpoints(
        self,
        name: str,
        vendor: str,
        site_ids: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Retrieve endpoint data for a specific application.

        Args:
            name (str)                       : The name of the application
            vendor (str)                     : The vendor of the application
            site_ids (str | list[str] | None): List of site ids to filter
            payload (dict[str, Any] | None)  : Payload to send to the endpoint

        Returns:
            DataType: Endpoint data based on the provided filters
        """

        if payload is None:
            payload = {}

        payload["applicationName"] = name
        payload["applicationVendor"] = vendor

        if "limit" not in payload:
            payload["limit"] = 1000

        if site_ids is not None:
            payload["siteIds"] = self._unify_str_list(site_ids)

        return self.fetch(S1Endpoint.APPLICATIONS_INVENTORY_ENDPOINTS, payload)

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

        if "limit" not in payload:
            payload["limit"] = 1000

        return self.fetch(S1Endpoint.APPLICATIONS_WITH_RISKS, payload)

    def cves(
        self,
        ids: "StrType | None" = None,
        severities: list[int] | None = None,
        site_ids: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Get known CVEs for applications installed on endpoints with 'Application Risk-enabled Agents'.

        Possible response messages
        200 - Success
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry.
        403 - Insufficient permissions

        Args:
            ids (str | list[str] | None)     : A list of CVE ids or partial ids to filter
            severities (list[int] | None)    : A list of severity numbers
            site_ids (str | list[str] | None): List of site ids to filter
            payload (dict[str, Any])         : Payload to send to the endpoint

        Returns:
            DataType: CVEs data based on the provided filters
        """

        if payload is None:
            payload = {}

        if ids is not None:
            payload["cveId__contains"] = self._unify_str_list(ids)

        if severities is not None:
            payload["severities"] = self._unify_str_list(
                [str(Severity.from_score(s)) for s in severities]
            )

        if site_ids is not None:
            payload["siteIds"] = self._unify_str_list(site_ids)

        if "limit" not in payload:
            payload["limit"] = 1000

        return self.fetch(S1Endpoint.APPLICATIONS_CVES, payload)

    def application_cves(
        self,
        ids: "StrType | None" = None,
        name: str | None = None,
        vendor: str | None = None,
        site_ids: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Retrieve CVEs for a specific appliation.

        Possible response messages
        200 - Success
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry.
        403 - Insufficient permissions

        Args:
            ids (str | list[str] | None)     : List of applications to include
            name (str | None)                : Application name, if application ids are not specified
            vendor (str | None)              : Application vendor, if application ids are not specified
            site_ids (str | list[str] | None): List of site ids to filter
            payload (dict[str, Any])         : Payload to send to the endpoint

        Returns:
            DataType: CVEs data based on the provided filters
        """

        if payload is None:
            payload = {}

        if ids is not None:
            payload["applicationIds"] = self._unify_str_list(ids)

        elif name is not None and vendor is not None:
            payload["applicationName"] = name
            payload["applicationVendor"] = vendor

        else:
            raise ValueError(
                f"{Context()}::You must provide either application IDs or specify an application name and vendor"
            )

        if site_ids is not None:
            payload["siteIds"] = self._unify_str_list(site_ids)

        return self.fetch(S1Endpoint.APPLICATIONS_APP_CVES, payload)

    # ****************************************************************
    # Methods: Groups

    def groups(
        self,
        names: "StrType | None" = None,
        site_ids: "StrType | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Get data of groups that match the filter.

        Possible response messages:
        200 - Success
        400 - Invalid user input received. See error details for further information
        401 - Unauthorized access - please sign in and retry

        Args:
            names (str | None)      : The name of the groups to retrieve
            site_ids (str | None)   : List of site IDs to filter
            payload (dict[str, Any]): Payload to send to the endpoint

        Returns:
            DataType: Groups data based on the provided filters
        """

        if payload is None:
            payload = {}

        if site_ids is not None:
            if not isinstance(site_ids, list):
                site_ids = [site_ids]

            payload["siteIds"] = site_ids

        if names is not None:
            res = []
            if not isinstance(names, list):
                names = [names]

            for name in names:
                payload["name"] = name

                req = self.fetch(S1Endpoint.GROUPS, payload)
                res.extend(req)

        else:
            res = self.fetch(S1Endpoint.GROUPS, payload)

        return res

    def group_policy(
        self,
        group_id: str,
    ) -> "DataType":
        """
        Retrieve the policy for the specified group.

        Possible response messages:
        200 - Success
        401 - Unauthorized access - please sign in and retry
        404 - Group not found

        Args:
            group_id (str): The id of the group which policy will be retrieved

        Returns:
            DataType: The policy of the specified group
        """

        return self.fetch(S1Endpoint.GROUPS_POLICY, {}, path_fmt={"groupId": group_id})

    def group_policy_update(
        self,
        group_id: "StrType",
        malicious_mitigation: "str | S1MitigationMode | None" = None,
        suspicious_mitigation: "str | S1MitigationMode | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Update the provided groups (by id) policy.

        Possible response messages:
        200 - Success
        400 - Invalid user input received. See error details for further information
        401 - Unauthorized access - please sign in and retry
        404 - Group not found

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
            if not isinstance(malicious_mitigation, S1MitigationMode):
                malicious_mitigation = S1MitigationMode[malicious_mitigation.upper()]

            payload["data"]["mitigationMode"] = str(malicious_mitigation)

        if suspicious_mitigation is not None:
            if not isinstance(suspicious_mitigation, S1MitigationMode):
                suspicious_mitigation = S1MitigationMode[suspicious_mitigation.upper()]

            payload["data"]["mitigationModeSuspicious"] = str(suspicious_mitigation)

        res = []
        for gid in group_id:
            # NOTE: Retrieving current group policy > May be unnecessary
            g_payload_data = self.fetch(
                S1Endpoint.GROUPS_POLICY,
                {},
                path_fmt={"groupId": gid},
            )[0]

            g_payload_data.update(payload["data"])

            res.extend(
                self.fetch(
                    S1Endpoint.GROUPS_POLICY_UPDATE,
                    payload={"data": g_payload_data},
                    path_fmt={"groupId": gid},
                )
            )

        return res

    def group_move_agent(
        self,
        group_id: str,
        agent_name: str | None = None,
        agent_ids: "StrType | None" = None,
        agent_filter: dict[str, Any] | None = None,
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
            group_id (str)                    : The ID of th group the agent must be moved in
            agent_name (str | None)           : The name of the agent that will be moved
            agent_ids (str | list[str] | None): A list of IDs of agents that will be moved
            agent_filter (dict[str, Any])     : A dictionary of filters to select agents that will be moved

        Returns:
            DataType: Response data
        """

        if agent_filter is None:
            agent_filter = {}

        if agent_ids is not None:
            agent_filter["ids"] = self._unify_str_list(agent_ids)

        elif agent_name is not None:
            agent_filter["computerName__contains"] = agent_name

        elif len(agent_filter.keys()) == 0:
            raise ValueError(f"{Context()}::No agent filter was specified")

        return self.fetch(
            S1Endpoint.GROUPS_MOVE_AGENTS,
            payload={"filter": agent_filter},
            path_fmt={"groupId": group_id},
        )

    # ****************************************************************
    # Methods: Sites

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

    def sites_by_name(
        self, site_name: "StrType", payload: dict[str, Any] | None = None
    ) -> "DataType":
        """
        Retrieve sites based on the provided name list.

        The response includes the IDs of Sites, which you can use in other commands.

        Possible response messages:
        200 - Success
        400 - Invalid user input received. See error details for further information.
        401 - Unauthorized access - please sign in and retry.

        Args:
            site_name (list[str])   : A list of site names to retrieve
            payload (dict[str, Any]): Payload to send to the endpoint

        Returns:
            DataType: Data of the site matching the provided ID
        """

        if not isinstance(site_name, list):
            site_name = [site_name]

        def _filter_by_name(site: dict[str, Any]) -> bool:
            return site["name"] in site_name

        return list(filter(_filter_by_name, self.sites(payload)))

    def sites_policy(
        self,
        site_id: str,
    ) -> "DataType":
        """
        Retrieve the policy for the specified site.

        Possible response messages:
        200 - Success
        401 - Unauthorized access - please sign in and retry
        404 - Group not found

        Args:
            site_id (str): The id of the site which policy will be retrieved

        Returns:
            DataType: The policy of the specified site
        """

        return self.fetch(S1Endpoint.SITES_POLICY, {}, path_fmt={"siteId": site_id})

    def site_policy_update(
        self,
        site_id: "StrType",
        malicious_mitigation: "str | S1MitigationMode | None" = None,
        suspicious_mitigation: "str | S1MitigationMode | None" = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Update the provided groups (by id) policy.

        Possible response messages:
        200 - Success
        400 - Invalid user input received. See error details for further information
        401 - Unauthorized access - please sign in and retry
        404 - Group not found

        Args:
            site_id (str | list[str])                      : Site to update the policy of
            malicious_mitigation (S1MitigationMode | None) : Malicious policy to set
            suspicious_mitigation (S1MitigationMode | None): Suspicious policy to set
            payload (dict[str, Any])                       : Payload to send

        Returns:
            DataType: Update result
        """

        if not isinstance(site_id, list):
            site_id = [site_id]

        if payload is None:
            payload = {}
            payload["data"] = {}

        if malicious_mitigation is not None:
            if not isinstance(malicious_mitigation, S1MitigationMode):
                malicious_mitigation = S1MitigationMode[malicious_mitigation.upper()]

            payload["data"]["mitigationMode"] = str(malicious_mitigation)

        if suspicious_mitigation is not None:
            if not isinstance(suspicious_mitigation, S1MitigationMode):
                suspicious_mitigation = S1MitigationMode[suspicious_mitigation.upper()]

            payload["data"]["mitigationModeSuspicious"] = str(suspicious_mitigation)

        res = []
        for sid in site_id:
            res.extend(
                self.fetch(S1Endpoint.SITES_POLICY_UPDATE, payload, path_fmt={"siteId": sid})
            )

        return res
