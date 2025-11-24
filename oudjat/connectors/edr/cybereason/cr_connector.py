"""A module to handle connection to Cybereason API."""

import json
import logging
import math
import re
from typing import Any, override
from urllib.parse import ParseResult, urlparse

import requests

from oudjat.connectors.connector import Connector
from oudjat.connectors.edr.cybereason.cr_endpoints import CybereasonEndpoint
from oudjat.utils import Context
from oudjat.utils.time_utils import TimeConverter
from oudjat.utils.types import StrType

from .cr_sensor_actions import CybereasonSensorAction
from .exceptions import (
    CybereasonAPIConnectionError,
    CybereasonAPIRequestError,
    CybereasonCredentialsError,
)


class CybereasonEntry(dict):
    """
    Handles some data transformations for ease of read. Cybereason entry inherits from dict.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, **kwargs: Any) -> None:
        """
        Create a new instance of CybereasonEntry.

        Args:
            entry_type (CybereasonEndpoint): type of the CybereasonEntry and which endpoint to assign to it
            kwargs (dict): keys and values of the base entry
        """

        cleaned_kwargs = {}
        for k, v in kwargs.items():
            formated_value = v
            # WARN: Convert unix time into readable string
            if "time" in k.lower():
                formated_value = TimeConverter.unixtime_to_str(v)

            # NOTE: Add short policy version
            elif k == "policyName":
                cleaned_kwargs["policyShort"] = formated_value
                policyShort = re.search(r"Detect|Protect", formated_value)

                if policyShort is not None:
                    cleaned_kwargs["policyShort"] = policyShort.group(0)

            # Handle malware file path
            elif k == "malwareDataModel" and isinstance(formated_value, dict):
                cleaned_kwargs["filePath"] = formated_value.get("filePath", None)

            cleaned_kwargs[k] = formated_value

        dict.__init__(self, **cleaned_kwargs)


class CybereasonConnector(Connector):
    """
    Handles interactions and queries to Cybereason API. Inherits from base Connector.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self, target: str, username: str | None = None, password: str | None = None, port: int = 443
    ) -> None:
        """
        Create a new instance of CybereasonConnector.

        Args:
            target (str)  : Cybereason URL
            username (str): Username to use for the connection
            password (str): Password to use for the connection
            port (int)    : Port number used for the connection
        """

        scheme = "http"
        if port == 443:
            scheme += "s"

        self.logger: "logging.Logger" = logging.getLogger(__class__.__name__)

        # Inject protocol if not found
        if not re.match(r"http(s?):", target):
            target = f"{scheme}://{target}"

        super().__init__(target=urlparse(target), username=username, password=password)

        self._DEFAULT_PAYLOAD: dict[str, Any] = {"filters": []}
        self._target: ParseResult = urlparse(
            f"{self._target.scheme}://{self._target.netloc}:{port}"
        )

        self.logger.debug(f"{Context()}::New CybereasonConnector - {self._target.netloc}")
        self._connection: "requests.Session | None" = None

    # ****************************************************************
    # Methods

    @override
    def connect(self) -> None:
        """
        Connect to Cybereason API using connector parameters.
        """

        context = Context()
        self.logger.info(f"{context}::Connecting to {self._target.netloc}")

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        session = requests.session()

        try:
            if not self._credentials:
                raise CybereasonCredentialsError(
                    f"{context}::Cannot connect to {self._target.netloc}, no credentials provided"
                )

            creds = {"username": self._credentials.username, "password": self._credentials.password}
            _ = session.post(
                f"{self._target.geturl()}/login.html", data=creds, headers=headers, verify=True
            )

        except CybereasonAPIConnectionError as e:
            raise CybereasonAPIConnectionError(
                f"{context}::An error occured while trying to connect to Cybereason API at {self.target.netloc}: {e}"
            )

        self.logger.info(f"{context}::Connected to {self._target.netloc}")
        self._connection = session

    def disconnect(self) -> None:
        """
        Close the session to Cybereason API.
        """

        if self._connection is not None:
            self._connection.close()
            self.logger.warning(f"{Context()}::Connection to {self._target.netloc} is now closed")

    def _endpoint_url(self, endpoint: CybereasonEndpoint) -> str:
        """
        Concatenate the base URL set to initialize the connector and the specified endpoint URL.

        Args:
            endpoint (CybereasonEndpoint): the endpoint the path will be concatenated to the main URL

        Returns:
            str: concatenated URL
        """

        return f"{self._target.geturl()}{endpoint.path}"

    @override
    def fetch(
        self,
        endpoint: "CybereasonEndpoint" = CybereasonEndpoint.SENSORS,
        endpoint_arg: str = "",
        payload: dict[str, Any] | None = None,
        attributes: list[str] | None = None,
    ) -> list["CybereasonEntry"]:
        """
        Run search in API.

        Args:
            endpoint (CybereasonEndpoint)  : Endpoint the search will be performed on
            endpoint_arg (str | None)      : Argument to append to the endpoint URI
            payload (dict[str, Any] | None): Payload to send to the endpoint
            attributes (list[str] | None)  : A list of arguments to keep for each entry

        Returns:
            list[CybereasonEntry]: search results
        """

        context = Context()

        if self._connection is None:
            raise CybereasonAPIConnectionError(
                f"{context}::Please initialize connection to {self._target.netloc} before attempting request"
            )

        if payload is None:
            payload = {}

        if attributes is None:
            attributes = endpoint.attributes

        self.logger.debug(f"{context}::Fetching {endpoint} data {payload}")

        res: list["CybereasonEntry"] = []
        try:
            req = self._connection.request(
                method=endpoint.method.name,
                url=f"{self._endpoint_url(endpoint)}/{endpoint_arg}",
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            )

            if req.status_code != 200:
                raise CybereasonAPIRequestError(f"API responded with status code {req.status_code}")

            req_json = req.json()
            if not isinstance(req_json, list):
                if "data" in req_json:
                    req_json = req_json.get("data", [])

                elif req_json.get(endpoint.name.lower(), None) is not None:
                    req_json = req_json.get(endpoint.name.lower())

                else:
                    req_json = [req_json]

            # Map to CybereasonEntry instances
            def map_cr_entry(element: dict[str, Any]) -> "CybereasonEntry":
                filtered_element = {k: v for k, v in element.items() if k in attributes}
                return CybereasonEntry(**filtered_element)

            res.extend(list(map(map_cr_entry, req_json)))

        except CybereasonAPIRequestError as e:
            raise CybereasonAPIRequestError(
                f"{context}::An error occured while retriving data from {self._endpoint_url(endpoint)}\n{e}"
            )

        return res

    # ****************************************************************
    # Methods: Policies

    def policy_edit(self, sensor_ids: StrType, policy_id: str) -> list["CybereasonEntry"]:
        """
        Edit policy for the given sensors.

        Args:
            sensor_ids (str | list[str]): list of sensors on which edit the policy
            policy_id (str)             : id of the policy to edit

        Returns:
            list[CybereasonEntry]: API query response
        """


        if not isinstance(sensor_ids, list):
            sensor_ids = [sensor_ids]

        payload = {"sensorsIds": sensor_ids, "keepManualOverrides": False}
        return self.fetch(endpoint=CybereasonEndpoint.POLICIES, endpoint_arg=f"{policy_id}/assign", payload=payload)

    # ****************************************************************
    # Methods: Sensors

    def sensors(
        self, payload: dict[str, Any] | None = None, limit: int | None = None
    ) -> list["CybereasonEntry"]:
        """
        Search for sensors using Cybereason API and based on search filter(s) and limit.

        Args:
            payload (dict): Query to run as a dictionary
            limit (int)   : Max number of search results

        Returns:
            list[CybereasonEntry]: search results
        """

        endpoint = CybereasonEndpoint.SENSORS

        # NOTE: Limit is the provided value or the endpoint limit if none provided
        limit = limit or endpoint.limit
        if payload is None:
            payload = self._DEFAULT_PAYLOAD

        payload["limit"] = limit
        payload["offset"] = 0

        res = []
        for i in range(0, math.ceil(limit / endpoint.limit)):
            payload["offset"] = i
            res.extend(self.fetch(endpoint=endpoint, payload=payload))

        print(f"{len(res)} {endpoint.name.lower()} found")
        return res

    def _sensor_action(
        self,
        action: CybereasonSensorAction,
        sensor_ids: StrType | None = None,
        payload: dict[str, Any] | None = None,
    ) -> list["CybereasonEntry"]:
        """
        Do a custom action on a list of sensors.

        Args:
            action (CybereasonSensorAction): Action to perform
            sensor_ids (str | list[str])   : List of sensors the action will be performed on
            payload (dict)                 : The query to perform represented by a dictionary that will be dumped
            *args                          : Any additional arguments
            **kwargs                       : Any additional kwargs

        Returns:
            list[CybereasonEntry]: API query response
        """

        if payload is None:
            payload = {}

        if sensor_ids is not None:
            if not isinstance(sensor_ids, list):
                sensor_ids = [sensor_ids]

            payload["sensorsIds"] = sensor_ids

        endpoint = CybereasonEndpoint.SENSORS_ACTION
        return self.fetch(
            endpoint=endpoint,
            endpoint_arg=f"{action.value}",
            payload=payload,
        )

    def sensor_remove_group(self, sensor_ids: StrType) -> list["CybereasonEntry"]:
        """
        Remove given sensors from group optionally specified.

        Args:
            sensor_ids (str | list[str]): list of sensors to remove the group from

        Returns:
            list[CybereasonEntry]: API query response
        """

        return self._sensor_action(
            action=CybereasonSensorAction.REMOVEFROMGROUP,
            sensor_ids=sensor_ids,
            payload=self._DEFAULT_PAYLOAD,
        )

    def sensor_assign_group(
        self, sensor_ids: StrType, group_id: str, payload: dict[str, Any] | None = None
    ) -> list["CybereasonEntry"]:
        """
        Assign given sensors to a group.

        Args:
            sensor_ids (str | list[str]): List of sensors the action will be performed on
            group_id (str)              : ID of the group the sensors will be assigned to
            payload (dict[str, Any])    : Payload to send to the endpoint

        Returns:
            list[CybereasonEntry]: API query response
        """

        if payload is None:
            payload = {}

        payload["argument"] = group_id

        return self._sensor_action(
            action=CybereasonSensorAction.ADDTOGROUP,
            sensor_ids=sensor_ids,
            payload=payload,
        )

    def sensor_restart(
        self, sensor_ids: StrType | None = None, payload: dict[str, Any] | None = None
    ) -> list["CybereasonEntry"]:
        """
        Restart given sensors.

        Args:
            sensor_ids (str | list[str]): IDs of the sensors to restart
            payload (dict[str, Any])    : Payload to send to the endpoint

        Returns:
            list[CybereasonEntry]: API query response
        """

        # NOTE: Handling Cybereason nonsense
        # When sensor IDs are provided, the filters must be empty
        # When sensor IDs are not provided, the filters must be provided at least as an empty array (WTF/FU/KILLME)
        if sensor_ids is None and payload is None:
            payload = self._DEFAULT_PAYLOAD

        elif sensor_ids is not None:
            payload = {}

        return self._sensor_action(
            action=CybereasonSensorAction.RESTART,
            sensor_ids=sensor_ids,
            payload=payload,
        )

    # ****************************************************************
    # Methods: Files

    def files(
        self, file_name: StrType, payload: dict[str, Any] | None = None, limit: int | None = None
    ) -> list["CybereasonEntry"]:
        """
        Search for specific file(s).

        Args:
            file_name (str | list[str]): Files to search
            payload (dict[str, Any])   : Filter to narrow down the search results
            limit (int)                : Limit of the search result numbers

        Returns:
            list[CybereasonEntry]: search results
        """

        endpoint = CybereasonEndpoint.FILES

        payload = payload or {}

        if not isinstance(file_name, list):
            file_name = [file_name]

        payload["limit"] = limit or endpoint.limit
        payload["fileFilters"] = [
            {"fieldName": "fileName", "values": file_name, "operator": "Equals"}
        ]

        batch_search = self.fetch(
            endpoint=endpoint,
            payload=payload,
        )

        res = []
        if len(batch_search) > 0:
            batch_id = batch_search[0].get("batchId", None)

            if batch_id is not None:
                res.extend(self.fetch(endpoint=endpoint, endpoint_arg=f"{batch_id}"))

        return res
