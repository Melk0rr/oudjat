import json
import math
import re
from typing import Dict, List, Union
from urllib.parse import urlparse

import requests

from oudjat.connectors import Connector
from oudjat.connectors.edr.cybereason import CybereasonEndpoint
from oudjat.utils import ColorPrint, unixtime_to_str

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

        Parameters:
            entry_type (CybereasonEndpoint): The type of the entry.
            **kwargs: Arbitrary keyword arguments to initialize the dictionary.
        """

        self.type = entry_type
        cleaned_kwargs = {}
        entry_attrs = entry_type.value.get("attributes")

        for k, v in kwargs.items():
            if k in entry_attrs:
                # WARN: Handle unix time
                if "time" in k.lower():
                    v = unixtime_to_str(v)

                # NOTE: Add short policy version
                if k == "policyName":
                    cleaned_kwargs["policyShort"] = v
                    shortPolicy = re.search(r"Detect|Protect", v)

                    if shortPolicy is not None:
                        cleaned_kwargs["policyShort"] = shortPolicy.group(0)

                # Handle malware file path
                if k == "malwareDataModel":
                    cleaned_kwargs["filePath"] = v.get("filePath", None)

                cleaned_kwargs[k] = v

        dict.__init__(self, **cleaned_kwargs)


class CybereasonConnector(Connector):
    """
    Cybereason connector inherinting from base Connector
    Handles interactions and queries to Cybereason API
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self, target: str, service_name: str = "OudjatCybereasonAPI", port: int = 443
    ) -> None:
        """
        Creates a new instance of CybereasonConnector

        Parameters:
            target (str): The target URL or hostname to connect to.
            service_name (str, optional): The name of the service. Used to register API credentials. Defaults to "OudjatCybereasonAPI".
            port (int, optional): The port number to use for the connection. Defaults to 443.
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
        Connects to API using connector parameters.

        This method initializes a session with the target API and authenticates using the provided credentials.
        It sets up necessary headers and attempts to post login credentials to the `/login.html` endpoint of the API.
        If successful, it prints a confirmation message in green color indicating the connection is established.

        Raises:
            ConnectionError: If there's an issue with establishing the connection to the Cybereason API.
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        session = requests.session()

        try:
            creds = {"username": self.credentials.username, "password": self.credentials.password}
            session.post(
                f"{self.target.geturl()}/login.html", data=creds, headers=headers, verify=True
            )

            ColorPrint.green(f"Connected to {self.target.netloc}")
            self.connection = session

        except ConnectionError as e:
            raise (
                f"An error occured while trying to connect to Cybereason API at {self.target}: {e}"
            )

    def disconnect(self) -> None:
        """
        Close session with target.

        This method closes the active session with the API endpoint and prints a yellow color message indicating that the connection is closed.
        """
        self.connection.close()
        ColorPrint.yellow(f"Connection to {self.target.netloc} is closed")

    def request(self, method: str, url: str, query: str = None) -> requests.models.Response:
        """
        Performs a request to given url using connector established connection.

        This method sends an HTTP request to the specified URL with the provided
        method (e.g., GET, POST). It includes necessary headers and uses the already
        established connection if available. If no active connection is found, it raises a ConnectionError.

        Args:
            method (str): The HTTP method for the request ('GET', 'POST', etc.).
            url (str): The target URL to send the request to.
            query (str, optional): Data payload for POST requests or query parameters for GET requests. Defaults to None.

        Returns:
            requests.models.Response: The response object from the API request.

        Raises:
            ConnectionError: If no connection has been established and required for making a request.
        """
        if self.connection is None:
            raise ConnectionError(
                f"Please initialize connection to {self.target.geturl()} before attempting request"
            )

        api_headers = {"Content-Type": "application/json"}
        return self.connection.request(
            method=method, url=f"{self.target.geturl()}/{url}", data=query, headers=api_headers
        )

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
        This function performs a search operation on a specified CybereasonEndpoint.

        Args:
            endpoint (CybereasonEndpoint)               : The specific endpoint where the search will be performed. This should be an instance of 'CybereasonEndpoint' representing the API endpoint to query.
            limit (int, optional)                       : Maximum number of results to return. Defaults to None.
            offset (int, optional)                      : Starting point for the search results. Defaults to 0.
            search_filter (List[Dict], optional)        : List of filters applied during the search operation. Each filter is a dictionary that defines the criteria for filtering. Defaults to None.
            endpoint_url_sfx (Union[int, str], optional): Suffix to append to the base endpoint URL. Defaults to None.
            endpoint_cnx_method (str, optional)         : Override for the HTTP method used to communicate with the API. If not provided, it defaults to the method defined in the endpoint configuration.
            **kwargs                                    : Additional keyword arguments that can be passed to the query construction or API request.

        Returns:
            List[Dict]: A list of dictionaries representing the search results after applying any filters and querying the specified endpoint. If there's an error during the API call, it returns None.
        """

        filter_opt = {"filters": []}
        if search_filter is not None:
            filter_opt["filters"] = search_filter

        query_content = {"limit": limit, "offset": offset, **filter_opt, **kwargs}
        query = json.dumps(query_content)

        endpoint_url = f"{endpoint.value.get('endpoint')}"

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
            ColorPrint.red(f"An error occured while querying {endpoint.value.get('endpoint')}\n{e}")

        return res

    def search(
        self, endpoint: str, search_filter: List[Dict] = None, limit: int = None, **kwargs
    ) -> List["CybereasonEntry"]:
        """
        Runs a search query in the API.

        This method allows you to perform searches on different endpoints of the Cybereason platform.

        Parameters:
            self (Any)                          : The instance of the class containing this method.
            endpoint (str)                      : A string representing the API endpoint to search on. Must be one of the Cybereason endpoints defined in `CybereasonEndpoint`.
            search_filter (List[Dict], optional): A list of dictionaries specifying filters for the search query. Defaults to None.
            limit (int, optional)               : An integer specifying the number of results to return per request. If not provided, it defaults to the endpoint's defined limit.
            **kwargs                            : Additional keyword arguments that can be passed to the underlying API call.

        Returns:
            List[CybereasonEntry]: A list of `CybereasonEntry` objects representing the results of the search query.

        Raises:
            ConnectionError : If no connection has been established with the Cybereason system.
            ValueError      : If an invalid endpoint is provided for searching.
        """

        if self.connection is None:
            raise ConnectionError(
                f"You must initiate connection to {self.target.netloc} before running search !"
            )

        endpoint = endpoint.upper()
        if endpoint not in CybereasonEndpoint.__members__:
            raise ValueError(f"Invalid Cybereason endpoint provided: {endpoint}")

        endpoint_attr = CybereasonEndpoint[endpoint]
        endpoint_search_limit = endpoint_attr.value.get("limit")

        # NOTE: Cybereason API returns data by pages
        # Set search limit based on page result number and max limit
        if limit is None:
            limit = endpoint_search_limit

        offset_mult = math.ceil(limit / endpoint_search_limit)

        res = []
        for i in range(0, offset_mult):
            search_i = self.endpoint_search(
                endpoint=endpoint_attr, search_filter=search_filter, limit=limit, offset=i, **kwargs
            )

            if search_i is not None:
                res.extend(search_i)

        print(f"{len(res)} {endpoint_attr.name.lower()} found")
        entries = list(map(lambda entry: CybereasonEntry(entry_type=endpoint_attr, **entry), res))

        return entries

    def search_files(
        self, file_name: Union[str, List[str]], search_filter: List[Dict] = None, limit: int = None
    ) -> List["CybereasonEntry"]:
        """
        This method allows you to search for one or multiple files based on their names.

        Parameters:
            self (Any)                          : The instance of the class containing this method.
            file_name (Union[str, List[str]])   : A string or list of strings representing the names of the files to search for.
            search_filter (List[Dict], optional): A list of dictionaries specifying additional filters for the search query. Defaults to None.
            limit (int, optional)               : An integer specifying the number of results to return per request. If not provided, it defaults to the `limit` value defined for the `FILES` endpoint in `CybereasonEndpoint`.

        Returns:
            List[CybereasonEntry]: A list of `CybereasonEntry` objects representing the files found.
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
                url=f"{CybereasonEndpoint.FILES.value.get('endpoint')}/{batch_id}",
            )

            if file_search_resp.content:
                res = json.loads(file_search_resp.content)
                res = res.get("data")

        return res

    def edit_policy(self, sensor_ids: Union[str, List[str]], policy_id: str) -> Dict:
        """
        This method allows you to update the policy settings for one or multiple sensors identified by their IDs.

        Parameters:
            self (Any)                        : The instance of the class containing this method.
            sensor_ids (Union[str, List[str]]): A string or list of strings representing the IDs of the sensors whose policies should be edited.
            policy_id (str)                   : A string representing the ID of the policy to be updated.

        Returns:
            Dict: A dictionary containing the response from the API after editing the policy.
        """

        if not isinstance(sensor_ids, list):
            sensor_ids = [sensor_ids]

        endpoint = CybereasonEndpoint.POLICIES

        policy_query = json.dumps({"sensorsIds": sensor_ids, "keepManualOverrides": False})
        policy_url = f"{endpoint.value.get('endpoint')}/{policy_id}/assign"

        policy_edit = self.request(
            method=endpoint.value.get("method"), url=policy_url, query=policy_query
        )

        return json.loads(policy_edit.content)

    def sensor_action(
        self,
        action: CybereasonSensorAction,
        sensor_ids: Union[str, List[str]],
        query: str,
        *args,
        **kwargs,
    ) -> Dict:
        """
        This method allows you to perform sensor actions (defined by `action`) on a list of sensors identified by their IDs.

        Args:
            action (CybereasonSensorAction)     : The type of action to perform, which is one of the actions defined in CybereasonSensorAction enum.
            sensor_ids (Union[str, List[str]])  : A single sensor ID or a list of sensor IDs for which the action should be performed.
            query (str)                         : Query parameters as a string that will be included in the request.

        Returns:
            Dict: The JSON response content from the API call is returned as a dictionary.
        """

        if not isinstance(sensor_ids, list):
            sensor_ids = [sensor_ids]

        endpoint = CybereasonEndpoint.SENSORS_ACTION

        query = self.request(
            method=endpoint.value.get("method"),
            url=f"{endpoint.value.get('endpoint')}/{action.value}",
            query=query,
        )

        return json.loads(query.content)

    def sensor_remove_group(self, sensor_ids: Union[str, List[str]]) -> Dict:
        """
        This method removes the specified sensors from any group they may be a part of. If no specific group is defined for removal, it defaults to removing them from an unspecified group.

        Args:
            sensor_ids (Union[str, List[str]]): A single sensor ID or a list of sensor IDs that should be removed from their group.

        Returns:
            Dict: The JSON response content from the API call is returned as a dictionary after removing sensors from their group.
        """

        if not isinstance(sensor_ids, list):
            sensor_ids = [sensor_ids]

        remove_query = json.dumps({"sensorsIds": sensor_ids, "filters": None})
        return self.sensor_action(
            action=CybereasonSensorAction.REMOVEFROMGROUP, sensor_ids=sensor_ids, query=remove_query
        )

    def sensor_assign_group(self, sensor_ids: Union[str, List[str]], groupId: str) -> Dict:
        """
        Assigns given sensors to a specified group.

        This method assigns the specified sensors to the group identified by `groupId`

        Args:
            sensor_ids (Union[str, List[str]])  : A single sensor ID or a list of sensor IDs that should be assigned to the specified group.
            groupId (str)                       : The unique identifier for the group to which the sensors will be assigned.

        Returns:
            Dict: The JSON response content from the API call is returned as a dictionary after assigning sensors to the specified group.
        """

        if not isinstance(sensor_ids, list):
            sensor_ids = [sensor_ids]

        assign_query = json.dumps({"sensorsIds": sensor_ids, "argument": groupId})
        return self.sensor_action(
            action=CybereasonSensorAction.ADDTOGROUP, sensor_ids=sensor_ids, query=assign_query
        )
