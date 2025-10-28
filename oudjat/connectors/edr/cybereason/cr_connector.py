"""A module to handle connection to Cybereason API."""

import json
import math
import re
from typing import Any, Callable, override
from urllib.parse import ParseResult, urlparse

import requests

from oudjat.connectors.connector import Connector
from oudjat.connectors.edr.cybereason.cr_endpoints import CybereasonEndpoint
from oudjat.utils.color_print import ColorPrint
from oudjat.utils.credentials import NoCredentialsError
from oudjat.utils.time_utils import TimeConverter
from oudjat.utils.types import DataType, StrType

from .cr_sensor_actions import CybereasonSensorAction


class CybereasonEntry(dict):
    """
    Handles some data transformations for ease of read. Cybereason entry inherits from dict.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, entry_type: "CybereasonEndpoint", **kwargs: Any) -> None:
        """
        Create a new instance of CybereasonEntry.

        Args:
            entry_type (CybereasonEndpoint): type of the CybereasonEntry and which endpoint to assign to it
            kwargs (dict): keys and values of the base entry
        """

        self.type: CybereasonEndpoint = entry_type
        cleaned_kwargs = {}
        entry_attrs = entry_type.attributes

        for k, v in kwargs.items():
            if k not in entry_attrs:
                continue

            formated_value = v
            # WARN: Convert unix time into readable string
            if "time" in k.lower():
                formated_value = TimeConverter.unixtime_to_str(v)

            # NOTE: Add short policy version
            if k == "policyName":
                cleaned_kwargs["policyShort"] = formated_value
                policyShort = re.search(r"Detect|Protect", formated_value)

                if policyShort is not None:
                    cleaned_kwargs["policyShort"] = policyShort.group(0)

            # Handle malware file path
            if k == "malwareDataModel" and isinstance(formated_value, dict):
                cleaned_kwargs["filePath"] = formated_value.get("filePath", None)

            cleaned_kwargs[k] = formated_value

        dict.__init__(self, **cleaned_kwargs)

    @staticmethod
    def from_search_result(
        res_elem: dict[str, Any], entry_type: "CybereasonEndpoint"
    ) -> "CybereasonEntry":
        """
        Create a new instance of CybereasonEntry from a search result.

        Args:
            res_elem (dict)                : search result element as a dictionary
            entry_type (CybereasonEndpoint): CybereasonEndpoint enum element matching the res element

        Returns:
            CybereasonEntry: new entry
        """

        return CybereasonEntry(entry_type=entry_type, **res_elem)


class CybereasonConnector(Connector):
    """
    Handles interactions and queries to Cybereason API. Inherits from base Connector.
    """

    # ****************************************************************
    # Attributes & Constructors

    _DEFAULT_PAYLOAD: dict[str, Any] = {"filters": []}

    def __init__(
        self, target: str, username: str | None = None, password: str | None = None, port: int = 443
    ) -> None:
        """
        Create a new instance of CybereasonConnector.

        Args:
            target (str)      : Cybereason URL
            username (str)    : Username to use for the connection
            password (str)    : Password to use for the connection
            port (int)        : Port number used for the connection
        """

        scheme = "http"
        if port == 443:
            scheme += "s"

        # Inject protocol if not found
        if not re.match(r"http(s?):", target):
            target = f"{scheme}://{target}"

        super().__init__(target=urlparse(target), username=username, password=password)

        self._target: ParseResult = urlparse(
            f"{self._target.scheme}://{self._target.netloc}:{port}"
        )
        self._connection: requests.Session | None = None

    # ****************************************************************
    # Methods

    @override
    def connect(self) -> None:
        """
        Connect to Cybereason API using connector parameters.
        """

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        session = requests.session()

        try:
            if not self._credentials:
                raise NoCredentialsError(pfx=f"{__class__.__name__}.connect::", target=self._target.netloc)

            creds = {"username": self._credentials.username, "password": self._credentials.password}
            _ = session.post(
                f"{self._target.geturl()}/login.html", data=creds, headers=headers, verify=True
            )

        except ConnectionError as e:
            raise ConnectionError(
                f"{__class__.__name__}.connect::An error occured while trying to connect to Cybereason API at {self.target}: {e}"
            )

        ColorPrint.green(f"Connected to {self._target.netloc}")
        self._connection = session

    def disconnect(self) -> None:
        """
        Close the session to Cybereason API.
        """

        if self._connection is not None:
            self._connection.close()
            ColorPrint.yellow(
                f"{__class__.__name__}.disconnect::Connection to {self._target.netloc} is now closed"
            )

    def get_complete_url(self, endpoint: CybereasonEndpoint) -> str:
        """
        Concatenate the base URL set to initialize the connector and the specified endpoint URL.

        Args:
            endpoint (CybereasonEndpoint): the endpoint the path will be concatenated to the main URL

        Returns:
            str: concatenated URL
        """

        return f"{self._target.geturl()}{endpoint.path}"

    def request(self, method: str, url: str, payload: str = "") -> requests.models.Response:
        """
        Perform a request to the given URL using established connection.

        Args:
            method (str)  : HTTP method used for the query (usually: GET, POST, PUT)
            url (str)     : Targeted query URL
            payload (str) : Dumped JSON query to run

        Returns:
            requests.models.Response: query response
        """

        if self._connection is None:
            raise ConnectionError(
                f"{__class__.__name__}.request::Please initialize connection to {self._target.geturl()} before attempting request"
            )

        if isinstance(payload, dict):
            payload = json.dumps(payload)

        api_headers = {"Content-Type": "application/json"}
        return self._connection.request(method=method, url=url, data=payload, headers=api_headers)

    @override
    def search(
        self,
        search_type: str,
        query: dict[str, Any] | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> list["CybereasonEntry"]:
        """
        Run search in API.

        Args:
            search_type (str) : endpoint the search will be performed on
            query (list[dict]): filter to narrow down the search results
            limit (int)       : limit the search result number
            kwargs (dict)     : additional arguments to pass to the final function

        Returns:
            list[CybereasonEntry]: search results
        """

        if self._connection is None:
            raise ConnectionError(
                f"{__class__.__name__}.search::You must initiate connection to {self._target.netloc} before running search !"
            )

        search_options: dict[str, Callable] = {
            "sensors": self.sensor_search,
            "files": self.file_search,
        }

        return search_options[search_type.lower()](query=query, limit=limit, **kwargs)

    def page_search(self, endpoint: "CybereasonEndpoint", query: str = "") -> DataType:
        """
        Search for entries in the specified Cybereason API endpoint.

        It processes the API response, handling Cybereason-specific data structures not uniformly aligned across responses.

        Args:
            endpoint (CybereasonEndpoint): The endpoint to which the query will be sent.
            query (str, optional): A search query string. Defaults to None.

        Returns:
            list[CybereasonEntry]: A list of entries retrieved from the API response.

        Raises:
            Exception: if anything goes wrong while processing json response
        """

        api_resp = self.request(
            method=endpoint.method, url=self.get_complete_url(endpoint), payload=query
        )

        res = []
        try:
            if api_resp.content:
                res = json.loads(api_resp.content)

                # NOTE: Handling Cybereason nonesense (response format not unified)
                if not isinstance(res, list):
                    if "data" in res:
                        res = res.get("data", [])

                    elif res.get(endpoint.name.lower()) is not None:
                        res = res.get(endpoint.name.lower())

        except Exception as e:
            ColorPrint.red(
                f"{__class__.__name__}.page_search::An error occured while querying {endpoint.path}\n{e}"
            )

        return res

    def sensor_search(
        self, query: dict[str, Any] | None = None, limit: int | None = None
    ) -> list["CybereasonEntry"]:
        """
        Search for sensors using Cybereason API and based on search filter(s) and limit.

        Args:
            query (dict): query to run as a dictionary
            limit (int) : max number of search results

        Returns:
            list[CybereasonEntry]: search results
        """

        endpoint = CybereasonEndpoint.SENSORS

        # NOTE: Limit is the provided value or the endpoint limit if none provided
        limit = limit or endpoint.limit
        payload: dict[str, Any] = {
            "limit": limit,
            "offset": 0,
            **(query or self._DEFAULT_PAYLOAD),
        }

        res = []
        for i in range(0, math.ceil(limit / endpoint.limit)):
            payload["offset"] = i
            search_i = self.page_search(endpoint=endpoint, query=json.dumps(payload))

            res.extend(search_i)

        print(f"{len(res)} {endpoint.name.lower()} found")
        return list(map(CybereasonEntry.from_search_result, res, [endpoint] * len(res)))

    def file_search(
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
        file_name = [file_name] if not isinstance(file_name, list) else file_name

        file_filters = [{"fieldName": "fileName", "values": file_name, "operator": "Equals"}]

        batch_search = self.page_search(
            endpoint=endpoint,
            query=str({"limit": limit or endpoint.limit, "fileFilters": file_filters, **payload}),
        )

        res = []
        if isinstance(batch_search, dict):
            batch_id = batch_search.get("batchId", None)

            if batch_id is not None:
                file_search_resp = self.request(
                    method="GET",
                    url=f"{self.get_complete_url(endpoint)}/{batch_id}",
                )

                res = (
                    json.loads(file_search_resp.content).get("data")
                    if file_search_resp.content is not None
                    else res
                )

        return res

    def edit_policy(self, sensor_ids: StrType, policy_id: str) -> dict[str, Any]:
        """
        Edit policy for the given sensors.

        Args:
            sensor_ids (str | list[str]): list of sensors on which edit the policy
            policy_id (str)             : id of the policy to edit

        Returns:
            dict: API query response
        """

        if not isinstance(sensor_ids, list):
            sensor_ids = [sensor_ids]

        endpoint = CybereasonEndpoint.POLICIES

        payload: str = json.dumps({"sensorsIds": sensor_ids, "keepManualOverrides": False})
        policy_url: str = f"{self._target.geturl()}/{endpoint.path}{policy_id}/assign"

        policy_edit = self.request(method=endpoint.method, url=policy_url, payload=payload)

        return json.loads(policy_edit.content)

    def sensor_action(
        self,
        action: CybereasonSensorAction,
        sensor_ids: StrType | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Do a custom action on a list of sensors.

        Args:
            action (CybereasonSensorAction): Action to perform
            sensor_ids (str | list[str])   : List of sensors the action will be performed on
            payload (dict)                 : The query to perform represented by a dictionary that will be dumped
            *args                          : Any additional arguments
            **kwargs                       : Any additional kwargs

        Returns:
            dict: API query response
        """

        sensor_ids = sensor_ids or []
        payload = payload or {}

        if not isinstance(sensor_ids, list):
            sensor_ids = [sensor_ids]

        endpoint = CybereasonEndpoint.SENSORS_ACTION
        api_resp = self.request(
            method=endpoint.method,
            url=f"{self._target.geturl()}/{endpoint.path}/{action.value}",
            payload=json.dumps({**payload, "sensorsIds": sensor_ids}),
        )

        return json.loads(api_resp.content)

    def sensor_remove_group(self, sensor_ids: StrType) -> dict[str, Any]:
        """
        Remove given sensors from group optionally specified.

        Args:
            sensor_ids (str | list[str]): list of sensors to remove the group from

        Returns:
            dict: API query response
        """

        return self.sensor_action(
            action=CybereasonSensorAction.REMOVEFROMGROUP,
            sensor_ids=sensor_ids,
            payload=self._DEFAULT_PAYLOAD,
        )

    def sensor_assign_group(self, sensor_ids: StrType, group_id: str) -> dict[str, Any]:
        """
        Assign given sensors to a group.

        Args:
            sensor_ids (str | list[str]): list of sensors the action will be performed on
            group_id (str)              : ID of the group the sensors will be assigned to

        Returns:
            dict: API query response
        """

        return self.sensor_action(
            action=CybereasonSensorAction.ADDTOGROUP,
            sensor_ids=sensor_ids,
            payload={"argument": group_id},
        )

    def sensor_restart(
        self, sensor_ids: StrType | None = None, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Restart given sensors.

        Args:
            sensor_ids (str | list[str]): IDs of the sensors to restart
            payload (dict[str, Any])    : Payload to send

        Returns:
            dict[str, Any]: API query response
        """

        # NOTE: Handling Cybereason nonsense
        # When sensor IDs are provided, the filters must be empty
        # When sensor IDs are not provided, the filters must be provided at least as an empty array (WTF/FU/KILLME)
        if sensor_ids is None and payload is None:
            payload = self._DEFAULT_PAYLOAD

        elif sensor_ids is not None:
            payload = {}

        return self.sensor_action(
            action=CybereasonSensorAction.RESTART,
            sensor_ids=sensor_ids,
            payload=payload,
        )
