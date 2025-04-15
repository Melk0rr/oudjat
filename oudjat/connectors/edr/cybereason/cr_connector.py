import json
import math
import re
from typing import Dict, List, Union
from urllib.parse import urlparse

import requests

from oudjat.connectors.connector import Connector
from oudjat.connectors.edr.cybereason.cr_endpoints import CybereasonEndpoint
from oudjat.utils.color_print import ColorPrint
from oudjat.utils.time_convertions import unixtime_to_str

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
        entry_attrs = entry_type.value.get("attributes")

        for k, v in kwargs.items():
            if k not in entry_attrs:
                continue

            formated_value = v
            # WARN: Convert unix time into readable string
            if "time" in k.lower():
                formated_value = unixtime_to_str(v)

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


class CybereasonConnector(Connector):
    """
    Cybereason connector inherinting from base Connector
    Handles interactions and queries to Cybereason API
    """

    # ****************************************************************
    # Attributes & Constructors

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
                f"CybereasonConnector.connect::An error occured while trying to connect to Cybereason API at {self.target}: {e}"
            )

        ColorPrint.green(f"Connected to {self.target.netloc}")
        self.connection = session

    def disconnect(self) -> None:
        """
        Closes the session to Cybereason API
        """

        self.connection.close()
        ColorPrint.yellow(f"Connection to {self.target.netloc} is closed")

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
                f"CybereasonConnector.request::Please initialize connection to {self.target.geturl()} before attempting request"
            )

        api_headers = {"Content-Type": "application/json"}
        return self.connection.request(method=method, url=url, data=query, headers=api_headers)

    def endpoint_search(
        self,
        endpoint: "CybereasonEndpoint",
        limit: int = None,
        offset: int = 0,
        search_filter: List[Dict] = None,
        endpoint_url_sfx: Union[int, str] = None,
        endpoint_cnx_method: str = None,
        **kwargs,
    ) -> List[Dict]:
        """
        Runs a search query on specific endpoint

        Args:
            endpoint (CybereasonEndpoint): Cybereason endpoint used for this search
            limit (int): search results limit
            offset (int): basically page number as CR may return results with pagination
            search_filter (List[Dict]): filter to narrow down search results
            endpoint_url_sfx (int | str): Optional URL sufix
            endpoint_cnx_method (str): HTTP connection method. By default it is retrieved from the endpoint parameters

        Returns:
            List[Dict]: search results
        """

        filter_opt = search_filter if search_filter is not None else {"filters": []}

        query_content = {"limit": limit, "offset": offset, **filter_opt, **kwargs}
        query = json.dumps(query_content)

        endpoint_url = f"{self.target.geturl()}{endpoint.value.get('endpoint')}"

        # INFO: optional sufix to include at the end of the URL
        if endpoint_url_sfx is not None:
            endpoint_url += f"/{endpoint_url_sfx}"

        # WARN: HTTP method varies between endpoints
        cnx_method = endpoint.value.get("method")

        if endpoint_cnx_method is not None:
            cnx_method = endpoint_cnx_method

        api_resp = self.request(method=cnx_method, url=endpoint_url, query=query)

        res = []
        try:
            if api_resp.content:
                res = json.loads(api_resp.content)

                # NOTE: Handling CR nonesense (response format not unified)
                if not isinstance(res, list):
                    if "data" in res:
                        if res.get("data") is None:
                            return None

                        res = res.get("data")

                    if res.get(endpoint.name.lower()) is not None:
                        res = res.get(endpoint.name.lower())

        except Exception as e:
            ColorPrint.red(
                f"CybereasonConnector.endpoint_search::An error occured while querying {endpoint.value.get('endpoint')}\n{e}"
            )

        return res

    def search(
        self, endpoint: CybereasonEndpoint, search_filter: List[Dict] = None, limit: int = None, **kwargs
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
                f"You must initiate connection to {self.target.netloc} before running search !"
            )

        endpoint_search_limit = endpoint.value.get("limit")

        # Set search limit
        limit = limit or endpoint_search_limit
        offset_mult = math.ceil(limit / endpoint_search_limit)

        res = []
        for i in range(0, offset_mult):
            search_i = self.endpoint_search(
                endpoint=endpoint, search_filter=search_filter, limit=limit, offset=i, **kwargs
            )

            if search_i is not None:
                res.extend(search_i)

        print(f"{len(res)} {endpoint.name.lower()} found")
        entries = list(map(lambda entry: CybereasonEntry(entry_type=endpoint, **entry), res))

        return entries

    def search_files(
        self, file_name: Union[str, List[str]], search_filter: List[Dict] = None, limit: int = None
    ) -> List["CybereasonEntry"]:
        """
        Searches for specific file(s)

        Args:
            file_name (str | List[str]): files to search
            search_filter (List[Dict]) : filter to narrow down the search results
            limit (int)                : limit of the search result numbers

        Returns:
            List[CybereasonEntry]: search results
        """

        if not isinstance(file_name, list):
            file_name = [file_name]

        file_filters = [{"fieldName": "fileName", "values": file_name, "operator": "Equals"}]

        if limit is None:
            limit = CybereasonEndpoint.FILES.value.get("limit")

        batch_search = self.endpoint_search(
            endpoint=CybereasonEndpoint.FILES,
            limit=limit,
            search_filter=search_filter,
            fileFilters=file_filters,
        )

        res = []
        batch_id = batch_search.get("batchId", None)

        if batch_id is not None:
            file_search_resp = self.request(
                method="GET",
                url=f"{self.target.geturl()}{CybereasonEndpoint.FILES.value.get('endpoint')}/{batch_id}",
            )

            if file_search_resp.content:
                res = json.loads(file_search_resp.content)
                res = res.get("data")

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
        policy_url = f"{self.target.geturl()}/{endpoint.value.get('endpoint')}{policy_id}/assign"

        policy_edit = self.request(
            method=endpoint.value.get("method"), url=policy_url, query=policy_query
        )

        return json.loads(policy_edit.content)

    def sensor_action(
        self,
        action: CybereasonSensorAction,
        sensor_ids: Union[str, List[str]],
        query_dict: Dict,
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

        query = self.request(
            method=endpoint.value.get("method"),
            url=f"{self.target.geturl()}/{endpoint.value.get('endpoint')}/{action.value}",
            query=query,
        )

        return json.loads(query.content)

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
            query_dict={"sensorsIds": sensor_ids, "filters": []},
        )

    def sensor_assign_group(self, sensor_ids: Union[str, List[str]], groupId: str) -> Dict:
        """
        Assigns given sensors to a group

        Args:
            sensor_ids (str | List[str]): list of sensors the action will be performed on
            groupId (str)               : ID of the group the sensors will be assigned to

        Returns:
            Dict: API query response
        """

        return self.sensor_action(
            action=CybereasonSensorAction.ADDTOGROUP,
            sensor_ids=sensor_ids,
            query_dict={"sensorsIds": sensor_ids, "argument": groupId},
        )

    def sensor_restart(self, sensor_ids: Union[str, List[str]]) -> Dict:
        """
        Restarts given sensors

        Args:
            sensor_ids (str | List[str]): IDs of the sensors to restart

        Returns:
            Dict: API query response
        """

        return self.sensor_action(
            action=CybereasonSensorAction.RESTART,
            sensor_ids=sensor_ids,
            query_dict={"sensorsIds": sensor_ids, "filters": []},
        )
