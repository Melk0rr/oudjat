"""A module handling Tenable.sc API connection."""

import re
from enum import Enum
from typing import Any, Callable, TypeAlias, override
from urllib.parse import ParseResult, urlparse

from tenable.sc import TenableSC

from oudjat.connectors.connector import Connector
from oudjat.control.data.data_filter import DataFilter
from oudjat.control.vulnerability.severity import Severity
from oudjat.utils import (
    ColorPrint,
    DataType,
    DatumDataType,
    DatumType,
    FilterTupleExtType,
    MyList,
    NoCredentialsError,
)

from .tsc_asset_list_types import TSCAssetListType
from .tsc_endpoints import TSCEndpoint
from .tsc_vuln_tools import TSCVulnTool

TSCFilter: TypeAlias = tuple[str, str, str]


class TSCBuiltinFilter(Enum):
    """
    A helper enumeration to list some built-in Tenable SC filters.
    """

    VULNS_EXPLOITABLE = ("exploitAvailable", "=", "true")
    VULNS_CRITICAL = ("severity", "=", "4")


class TenableSCConnector(Connector):
    """
    A class to handle Tenable.sc API interactions (inherits from Connector).

    For details, see : https://pytenable.readthedocs.io/en/stable/index.html.
    """

    # ****************************************************************
    # Attributes & Constructors

    def __init__(
        self, target: str, username: str | None = None, password: str | None = None, port: int = 443
    ) -> None:
        """
        Create a new instance of TenableSCConnector.

        Args:
            target (str)      : Tenable.sc appliance URL
            username (str)    : Username to use for the connection
            password (str)    : Password to use for the connection
            port (int)        : Port number
        """

        scheme = "http"
        if port == 443:
            scheme += "s"

        if not re.match(r"http(s?):", target):
            target = f"{scheme}://{target}"

        self._target: ParseResult
        super().__init__(target=urlparse(target), username=username, password=password)

        self._connection: TenableSC
        self._repos: list[str] | None = None

    # ****************************************************************
    # Methods

    @property
    def repos(self) -> list[str] | None:
        """
        Return repositories list.

        Returns:
            list[str] : list of repos defined on security center
        """

        return self._repos

    def _severity_filter(self, *severities: list[int]) -> TSCFilter:
        """
        Return a severity filter based on the provided severities.

        Args:
            severities (list[str]) : severities to include in the filter (see cve.py)
        """

        severity_str: str = ",".join(
            [f"{Severity.from_score(sev).score}" for sev in list(*severities)]
        )
        return (*TSCBuiltinFilter.VULNS_CRITICAL.value[:2], severity_str)

    # INFO: Base connector methods
    @override
    def connect(self) -> None:
        """
        Connect to API using connector parameters.

        Raises:
            NoCredentialsError: If no credentials were provided to connect to the target
            ConnectionError: If anything goes wrong while connecting to the target
        """

        if self._credentials is None:
            raise NoCredentialsError(
                f"{__class__.__name__}.connect::No credentials provided to connect to {self._target.netloc}"
            )

        try:
            self._connection = TenableSC(
                host=self._target.netloc,
                access_key=self._credentials.username,
                secret_key=self._credentials.password,
            )

            ColorPrint.green(f"Connected to {self._target.netloc}")
            self._repos = self._connection.repositories.list()

        except ConnectionError as e:
            raise ConnectionError(
                f"{__class__.__name__}.connect::Could not connect to {self._target.netloc}\n{e}"
            )

    def disconnect(self) -> None:
        """
        Disconnect from API.
        """

        del self._connection
        self._connection = None
        self._repos = []

    @override
    def fetch(
        self,
        endpoint: "TSCEndpoint" = TSCEndpoint.VULNS,
        payload: "DatumType | None" = None,
        *args: Any,
        **kwargs: Any,
    ) -> "DataType":
        """
        Search the API for elements.

        Args:
            endpoint (TSCEndpoint)  : "Endpoint" to hit, basically which API action will be performed
            payload (dict[str, Any]): Payload to send to the provided endpoint
            *args (Any)             : Anything to pass to further search method
            **kwargs (Any)          : Anything to pass to further search method

        Returns:
            DataType: Data based on the provided endpoint and payload

        Raises:
            ConnectionError: If no connection is initialized
            ConnectionError: If anything goes wrong while fetching data from the target endpoint
        """

        if self.connection is None:
            raise ConnectionError(
                f"{__class__.__name__}.fetch::Can't retrieve data from {self._target.netloc}/{endpoint.value} if no connection is initialized"
            )

        if payload is None:
            payload = {}

        res = []
        try:
            endpoint_func: Callable[..., "DatumDataType"] = getattr(
                self._connection, endpoint.value
            )
            req = endpoint_func(*args, **payload, **kwargs)

            MyList.append_flat(res, req)

        except ConnectionError as e:
            raise ConnectionError(
                f"{__class__.__name__}.fetch::Could not retrieve data from {self._target.netloc}/{endpoint.value}\n{e}"
            )

        return res

    # ****************************************************************
    # Methods: Vulns

    def vulns(
        self,
        *severities: list[int],
        tool: TSCVulnTool = TSCVulnTool.VULNDETAILS,
        exploitable: bool = True,
        payload: dict[str, Any] | None = None,
    ) -> DataType:
        """
        Retrieve the current vulnerabilities.

        Args:
            severities (List[str])         : Vuln severities to include
            tool (TSCVulnTool)             : Tool to use for the search
            exploitable (bool)             : Wheither to search only for exploitable vulnerabilities or not
            payload (dict[str, Any] | None): Payload to send to the endpoint

        Returns:
            DataType: Vulnerabilities matching arguments
        """

        if payload is None:
            payload = {}

        payload["tool"] = tool.value

        filters: list["TSCFilter"] = []
        if exploitable:
            filters.append(TSCBuiltinFilter.VULNS_EXPLOITABLE.value)

        filters.append(self._severity_filter(*severities))
        return self.fetch(endpoint=TSCEndpoint.VULNS, *filters, payload=payload)

    # ****************************************************************
    # Methods: Asset lists

    def asset_lists_create(
        self,
        name: str,
        list_type: TSCAssetListType = TSCAssetListType.COMBINATION,
        description: str | None = None,
        ips: list[str] | None = None,
        dns_names: list[str] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Create a new asset list.

        Args:
            name (str)                     : Name of the asset list
            list_type (TSCAssetListType)   : Type of the asset list (see tsc_asset_list_types.py for details)
            description (str | None)       : Asset list description
            ips: (list[str] | None)        : A list of ip addresses to associate with the list
            dns_names: (list[str] | None)  : A list of dns names to associate with the list
            payload (dict[str, Any] | None): Payload to send to the endpoint

        Returns:
            DataType: Data containing the details of the created asset lists
        """

        if payload is None:
            payload = {}

        payload["name"] = name
        payload["list_type"] = list_type.value

        if description:
            payload["description"] = description

        if ips:
            payload["ips"] = ips

        if dns_names:
            payload["dns_names"] = dns_names

        return self.fetch(endpoint=TSCEndpoint.ASSETS_CREATE, payload=payload)

    def asset_lists_delete(self, list_id: int | list[int]) -> "DataType":
        """
        Delete an asset list based on given id.

        Args:
            list_id (int | List[int]) : list of ids of the asset lists to delete

        Returns:
            DataType: Data containing the details of the deleted asset lists
        """

        if not isinstance(list_id, list):
            list_id = [list_id]

        res = []
        for lid in list_id:
            res.extend(self.fetch(endpoint=TSCEndpoint.ASSETS_DELETE, id=lid))

        return res

    def asset_lists(
        self,
        list_filter: FilterTupleExtType | None = None,
        fields: list[str] | None = None,
    ) -> "DataType":
        """
        Retrieve a list of asset lists with minimal informations like list ids.

        Args:
            list_filter (Tuple[str, str, any]): filter to apply to the listing
            fields (list[str] | None)      : A list of attributes to return for each asset lists

        Returns:
            DataType: Data of asset lists matching provided filter
        """

        payload = {}

        if fields:
            payload["fields"] = fields

        asset_lists = self.fetch(endpoint=TSCEndpoint.ASSETS, payload=payload)
        if len(asset_lists) > 0:
            asset_lists = asset_lists[0].get("usable", [])

        if list_filter:
            asset_lists = DataFilter.filter_data(
                data_to_filter=asset_lists, filters=DataFilter.gen_from_tuple(list_filter)
            )

        return asset_lists

    def asset_lists_details(
        self,
        list_id: int | list[int],
        fields: list[str] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Return the details of one or more asset lists.

        Args:
            list_id (int | list[int])      : List of ids matching the asset lists to retrieve
            fields (list[str] | None)      : A list of attributes to return for each asset lists
            payload (dict[str, Any] | None): Payload to send to the endpoint

        Returns:
            DataType: Data containing the details of the assets matching the provided IDs
        """

        if payload is None:
            payload = {}

        if fields:
            payload["fields"] = fields

        if not isinstance(list_id, list):
            list_id = [list_id]

        list_details = []
        for lid in list_id:
            list_details.extend(
                self.fetch(endpoint=TSCEndpoint.ASSETS_DETAILS, payload={**payload, "id": lid})
            )

        return list_details

    # TODO: Edit asset list

    # ****************************************************************
    # Methods: Scans

    def scans(
        self,
        scan_filter: "FilterTupleExtType | None" = None,
        fields: list[str] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Retrieve a list of scans with minimal information like scan ids.

        Args:
            scan_filter (Tuple[str, str, any]): Filter to apply to the listing
            fields (list[str] | None)         : A list of attributes to return for each scan
            payload (dict[str, Any] | None)   : Payload to send to the endpoint

        Returns:
            DataType: Data of the scans matching the provided filters
        """

        if payload is None:
            payload = {}

        if fields:
            payload["fields"] = fields

        scan_list = self.fetch(endpoint=TSCEndpoint.SCANS, payload=payload)

        if len(scan_list) > 0:
            scan_list = scan_list[0].get("usable", [])

        if scan_filter:
            scan_list = DataFilter.filter_data(
                data_to_filter=scan_list, filters=DataFilter.gen_from_tuple(scan_filter)
            )

        return scan_list

    def scans_details(self, scan_id: int | list[int]) -> "DataType":
        """
        Return the details of one or more scans.

        Args:
            scan_id (int | list[int]): One or more scan id to retrieve

        Returns:
            DataType: Data containing the details of the scans matching provided IDs
        """

        if not isinstance(scan_id, list):
            scan_id = [scan_id]

        scan_details = []
        for sid in scan_id:
            scan_details.extend(self.fetch(endpoint=TSCEndpoint.SCANS_DETAILS, id=sid))

        return scan_details

    def scans_delete(self, scan_id: int | list[int]) -> "DataType":
        """
        Delete an asset list based on given id.

        Args:
            scan_id (int | list[int]) : one or more scan id to delete

        Return:
            DataType: Data containing the details of the deleted scans
        """

        if not isinstance(scan_id, list):
            scan_id = [scan_id]

        res = []
        for sid in scan_id:
            res.extend(self.fetch(endpoint=TSCEndpoint.SCANS_DELETE, id=sid))

        return res

    def scans_create(
        self,
        name: str,
        repo_id: int,
        asset_lists: list[int] | None = None,
        description: str | None = None,
        schedule: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> "DataType":
        """
        Create a new scan.

        Args:
            name (str)                      : Name of the scan
            repo_id (int)                   : Repository id for the scan
            asset_lists (list[int] | None)  : The asset lists ids to run the scan against
            description (str | None)        : Scan description
            schedule (dict[str, str] | None): Schedule dictionary
            payload (dict[str, Any] | None) : Payload to send to the endpoint

        Returns:
            DataType: Data containing the created scan details
        """

        if payload is None:
            payload = {}

        payload["name"] = name
        payload["repo"] = repo_id

        if asset_lists:
            payload["asset_lists"] = asset_lists

        if description:
            payload["description"] = description

        if schedule:
            payload["schedule"] = schedule

        return self.fetch(endpoint=TSCEndpoint.SCANS_CREATE, payload=payload)
