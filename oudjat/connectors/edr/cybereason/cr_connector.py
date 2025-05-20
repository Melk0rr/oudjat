import json
import math
import re
from typing import Callable, Dict, List, Union
from urllib.parse import urlparse

import requests

from oudjat.connectors.connector import Connector
from oudjat.connectors.edr.cybereason.cr_endpoints import CybereasonEndpoint
from oudjat.utils.color_print import ColorPrint
from oudjat.utils.time_utils import TimeConverter

from .cr_sensor_actions import CybereasonSensorAction


class CybereasonEntry(dict):
    """
    Cybereason entry inherits from dict
    Handles some data transformations for ease of read
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(self, entry_type: "CybereasonEndpoint", **kwargs) -> None:
        """
        Creates a new instance of CybereasonEntry

        Args:
            entry_type (CybereasonEndpoint): type of the CybereasonEntry and which endpoint to assign to it
        """

        self.type = entry_type
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
            if k == "malwareDataModel":
                cleaned_kwargs["filePath"] = formated_value.get("filePath", None)

            cleaned_kwargs[k] = formated_value

        dict.__init__(self, **cleaned_kwargs)

    @staticmethod
    def from_search_result(res_elem: Dict, entry_type: "CybereasonEndpoint") -> "CybereasonEntry":
        """
        Creates a new instance of CybereasonEntry from a search result

        Args:
            res_elem (Dict)                : search result element as a dictionary
            entry_type (CybereasonEndpoint): CybereasonEndpoint enum element matching the res element

        Returns:
            CybereasonEntry: new entry
        """

        return CybereasonEntry(entry_type=entry_type, **res_elem)


class CybereasonConnector(Connector):
    """
    Cybereason connector inherinting from base Connector
    Handles interactions and queries to Cybereason API
    """

    # ****************************************************************
    # Attributes & Constructors

    DEFAULT_QUERY_DICT = {"filters": []}

    def __init__(self, target: str, service_name: str = "OudjatCybereasonAPI", port: int = 443):
        """
        Creates a new instance of CybereasonConnector

        Args:
            target (str)      : Cybereason URL
            service_name (str): name of the service, used to register credentials
            port (int)        : port number used for the connection
        """

        scheme = "http"
        if port == 443:
            scheme += "s"

        # Inject protocol if not found
        if not re.match(r"http(s?):", target):
            target = f"{scheme}://{target}"

        super().__init__(target=urlparse(target), service_name=service_name, use_credentials=True)

        self.target = urlparse(f"{self.target.scheme}://{self.target.netloc}:{port}")

    # ****************************************************************
    # Methods

    def connect(self) -> None:
        """
        Connects to Cybereason API using connector parameters
        """

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        session = requests.session()

        try:
            creds = {"username": self.credentials.username, "password": self.credentials.password}
            session.post(
                f"{self.target.geturl()}/login.html", data=creds, headers=headers, verify=True
            )

        except ConnectionError as e:
            raise (
                f"{__class__.__name__}.connect::An error occured while trying to connect to Cybereason API at {self.target}: {e}"
            )

        ColorPrint.green(f"Connected to {self.target.netloc}")
        self.connection = session

    def disconnect(self) -> None:
        """
        Closes the session to Cybereason API
        """

        self.connection.close()
        ColorPrint.yellow(f"Connection to {self.target.netloc} is closed")

    def get_complete_url(self, endpoint: CybereasonEndpoint) -> str:
        """
        Concatenates the base URL set to initialize the connector and the specified endpoint URL

        Args:
            endpoint (CybereasonEndpoint): the endpoint the path will be concatenated to the main URL

        Returns:
            str: concatenated URL
        """

        return f"{self.target.geturl()}{endpoint.path}"

    def request(self, method: str, url: str, query: str = None) -> requests.models.Response:
        """
        Performs a request to the given URL using established connection

        Args:
            method (str): HTTP method used for the query (usually: GET, POST, PUT)
            url (str)   : targeted query URL
            query (str) : dumped JSON query to run

        Returns:
            requests.models.Response: query response
        """

        if self.connection is None:
            raise ConnectionError(
                f"{__class__.__name__}.request::Please initialize connection to {self.target.geturl()} before attempting request"
            )

        if type(query) is dict:
            query = json.dumps(query)

        api_headers = {"Content-Type": "application/json"}
        return self.connection.request(method=method, url=url, data=query, headers=api_headers)

    def search(
        self, search_type: str, query: Dict = None, limit: int = None, **kwargs
    ) -> List["CybereasonEntry"]:
        """
        Runs search in API

        Args:
            endpoint (str)            : endpoint the search will be performed on
            search_filter (List[Dict]): filter to narrow down the search results
            limit (int)               : limit the search result number

        Returns:
            List[CybereasonEntry]: search results
        """

        if self.connection is None:
            raise ConnectionError(
                f"{__class__.__name__}.search::You must initiate connection to {self.target.netloc} before running search !"
            )

        search_options: Dict[str, Callable] = {
            "sensors": self.sensor_search,
            "files": self.file_search,
        }

        return search_options[search_type.lower()](query=query, limit=limit, **kwargs)

    def page_search(
        self, endpoint: "CybereasonEndpoint", query: str = None
    ) -> List["CybereasonEntry"]:
        """
        Searches for entries in the specified Cybereason API endpoint.
        It processes the API response, handling Cybereason-specific data structures not uniformly aligned across responses.

        Args:
            endpoint (CybereasonEndpoint): The endpoint to which the query will be sent.
            query (str, optional): A search query string. Defaults to None.

        Returns:
            List[CybereasonEntry]: A list of entries retrieved from the API response.

        Raises:
            Exception: if anything goes wrong while processing json response
        """

        api_resp = self.request(
            method=endpoint.method, url=self.get_complete_url(endpoint), query=query
        )

        res = []
        try:
            if api_resp.content:
                res = json.loads(api_resp.content)

                # NOTE: Handling Cybereason nonesense (response format not unified)
                if not isinstance(res, list):
                    if "data" in res:
                        if res.get("data") is None:
                            return None

                        res = res.get("data")

                    if res.get(endpoint.name.lower()) is not None:
                        res = res.get(endpoint.name.lower())

        except Exception as e:
            ColorPrint.red(
                f"{__class__.__name__}.page_search::An error occured while querying {endpoint.path}\n{e}"
            )

        return res

    def sensor_search(self, query: Dict = None, limit: int = None) -> List["CybereasonEntry"]:
        """
        Searches for sensors using Cybereason API and based on search filter(s) and limit

        Args:
            search_filter (Dict): search filter(s) as a dictionary
            limit (int)         : max number of search results

        Returns:
            List[CybereasonEntry]: search results
        """

        endpoint = CybereasonEndpoint.SENSORS

        # NOTE: Limit is the provided value or the endpoint limit if none provided
        limit = limit or endpoint.limit
        offset_mult = math.ceil(limit / endpoint.limit)

        built_filter = query if query is not None else self.DEFAULT_QUERY_DICT
        built_query = {"limit": limit, "offset": 0, **built_filter}

        res = []
        for i in range(0, offset_mult):
            built_query["offset"] = i
            search_i = self.page_search(endpoint=endpoint, query=json.dumps(built_query))

            if search_i is not None:
                res.extend(search_i)

        print(f"{len(res)} {endpoint.name.lower()} found")
        return list(map(CybereasonEntry.from_search_result, res, [endpoint] * len(res)))

    def file_search(
        self, file_name: Union[str, List[str]], query: Dict = None, limit: int = None
    ) -> List["CybereasonEntry"]:
        """
        Searches for specific file(s)

        Args:
            file_name (str | List[str]): files to search
            query (Dict)               : filter to narrow down the search results
            limit (int)                : limit of the search result numbers

        Returns:
            List[CybereasonEntry]: search results
        """

        endpoint = CybereasonEndpoint.FILES

        file_name = [file_name] if not isinstance(file_name, list) else file_name
        limit = limit or endpoint.limit

        file_filters = [{"fieldName": "fileName", "values": file_name, "operator": "Equals"}]
        built_query = {"limit": limit, "fileFilters": file_filters, **query}

        batch_search = self.page_search(
            endpoint=endpoint,
            limit=limit,
            query=built_query,
        )

        batch_id = batch_search.get("batchId", None)

        res = []
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

    def edit_policy(self, sensor_ids: Union[str, List[str]], policy_id: str) -> Dict:
        """
        Edit policy for the given sensors

        Args:
            sensor_ids (str | List[str]): list of sensors on which edit the policy
            policy_id (str)             : id of the policy to edit

        Returns:
            Dict: API query response
        """

        if not isinstance(sensor_ids, list):
            sensor_ids = [sensor_ids]

        endpoint = CybereasonEndpoint.POLICIES

        policy_query = json.dumps({"sensorsIds": sensor_ids, "keepManualOverrides": False})
        policy_url = f"{self.target.geturl()}/{endpoint.path}{policy_id}/assign"

        policy_edit = self.request(method=endpoint.method, url=policy_url, query=policy_query)

        return json.loads(policy_edit.content)

    def sensor_action(
        self,
        action: CybereasonSensorAction,
        sensor_ids: Union[str, List[str]] = [],
        query_dict: Dict = {},
        *args,
        **kwargs,
    ) -> Dict:
        """
        Do a custom action on a list of sensors

        Args:
            action (CybereasonSensorAction): action to perform
            sensor_ids (str | List[str])   : list of sensors the action will be performed on
            query_dict (Dict)              : the query to perform represented by a dictionary that will be dumped
            *args                          : any additional arguments
            **kwargs                       : any additional kwargs

        Returns:
            Dict: API query response
        """

        if not isinstance(sensor_ids, list):
            sensor_ids = [sensor_ids]

        query = json.dumps({**query_dict, "sensorsIds": sensor_ids})
        endpoint = CybereasonEndpoint.SENSORS_ACTION

        api_resp = self.request(
            method=endpoint.method,
            url=f"{self.target.geturl()}/{endpoint.path}/{action.value}",
            query=query,
        )

        return json.loads(api_resp.content)

    def sensor_remove_group(self, sensor_ids: Union[str, List[str]]) -> Dict:
        """
        Removes given sensors from group optionally specified

        Args:
            sensor_ids (str | List[str]): list of sensors to remove the group from

        Returns:
            Dict: API query response
        """

        return self.sensor_action(
            action=CybereasonSensorAction.REMOVEFROMGROUP,
            sensor_ids=sensor_ids,
            query_dict=self.DEFAULT_QUERY_DICT,
        )

    def sensor_assign_group(self, sensor_ids: Union[str, List[str]], group_id: str) -> Dict:
        """
        Assigns given sensors to a group

        Args:
            sensor_ids (str | List[str]): list of sensors the action will be performed on
            group_id (str)              : ID of the group the sensors will be assigned to

        Returns:
            Dict: API query response
        """

        return self.sensor_action(
            action=CybereasonSensorAction.ADDTOGROUP,
            sensor_ids=sensor_ids,
            query_dict={"argument": group_id},
        )

    def sensor_restart(self, sensor_ids: Union[str, List[str]] = None, query: Dict = None) -> Dict:
        """
        Restarts given sensors

        Args:
            sensor_ids (str | List[str]): IDs of the sensors to restart

        Returns:
            Dict: API query response
        """

        # NOTE: Handling Cybereason nonsense
        # When sensor IDs are provided, the filters must be empty
        # When sensor IDs are not provided, the filters must be provided at least as an empty array (WTF/FU/KILLME)
        if sensor_ids is None and query is None:
            query = self.DEFAULT_QUERY_DICT

        elif sensor_ids is not None:
            query = {}

        return self.sensor_action(
            action=CybereasonSensorAction.RESTART,
            sensor_ids=sensor_ids,
            query_dict=query,
        )
