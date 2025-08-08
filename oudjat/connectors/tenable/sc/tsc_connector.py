"""A module handling Tenable.sc API connection."""

import re
from typing import Any, Callable, Literal, override
from urllib.parse import ParseResult, urlparse

from tenable.sc import TenableSC

from oudjat.connectors.connector import Connector
from oudjat.control.data.data_filter import DataFilter
from oudjat.control.vulnerability.severity import Severity
from oudjat.utils.color_print import ColorPrint
from oudjat.utils.types import FilterTupleExtType

from .tsc_asset_list_types import TSCAssetListType
from .tsc_vuln_tools import TSCVulnTool


class TenableSCConnector(Connector):
    """
    A class to handle Tenable.sc API interactions (inherits from Connector).

    For details, see : https://pytenable.readthedocs.io/en/stable/index.html.
    """

    # ****************************************************************
    # Attributes & Constructors

    BUILTIN_FILTERS: dict[str, tuple[str, str, str]] = {
        "exploitable": ("exploitAvailable", "=", "true")
    }

    def __init__(
        self, target: str, service_name: str = "OudjatTenableSCAPI", port: int = 443
    ) -> None:
        """
        Create a new instance of TenableSCConnector.

        Args:
            target (str)      : Tenable.sc appliance URL
            service_name (str): service name used to register credentials
            port (int)        : port number
        """

        scheme = "http"
        if port == 443:
            scheme += "s"

        if not re.match(r"http(s?):", target):
            target = f"{scheme}://{target}"

        super().__init__(target=target, service_name=service_name, use_credentials=True)
        self.parsed_target: ParseResult = urlparse(target)
        self.parsed_target = urlparse(f"{self.parsed_target.scheme}://{self.parsed_target.netloc}")

        self.connection: TenableSC = None
        self.repos: list[str] | None = None

    # ****************************************************************
    # Methods

    # INFO: Getters
    def get_repos(self) -> list[str] | None:
        """
        Return repositories list.

        Returns:
            List : list of repos defined on security center
        """

        return self.repos

    # INFO: Base connector methods
    @override
    def connect(self) -> None:
        """
        Connect to API using connector parameters.
        """

        connection: TenableSC | None = None
        try:
            if self._credentials is not None:
                connection = TenableSC(
                    host=self.parsed_target.netloc,
                    access_key=self._credentials.username,
                    secret_key=self._credentials.password,
                )

            ColorPrint.green(f"Connected to {self.parsed_target.netloc}")
            self.connection = connection
            self.repos = self.connection.repositories.list()

        except Exception as e:
            raise e

    def check_connection(self) -> None:
        """
        Check if the connection is initialized.

        Raises:
            ConnectionError: if connector connection is not initialized
        """

        if self.connection is None:
            raise ConnectionError(
                f"{__class__.__name__}.check_connection::Can't create asset list if connection is not initialized"
            )

    def disconnect(self) -> None:
        """
        Disconnect from API.
        """

        del self.connection
        self.connection = None
        self.repos = None

    @override
    def search(self, search_type: str = "VULNS", *args: Any, **kwargs: Any) -> list[object]:
        """
        Search the API for elements.

        Args:
            search_type (str): search type (VULNS | ASSETS | SCANS)
            *args (List)     : anything to pass to further search method
            **kwargs (Dict)  : anything to pass to further search method

        Returns:
            List: search result depending on search type

        Raises:
            Exception: if something goes wrong with the search
        """

        self.check_connection()

        search_type = search_type.upper()
        search_options: dict[str, Callable] = {
            "ASSETS": self.list_asset_lists,
            "SCANS": self.list_scans,
            "VULNS": self.search_vulns,
        }

        if search_type not in search_options.keys():
            raise ValueError(f"{__class__.__name__}.search::Invalid search type {search_type}")

        search: list[dict[str, Any]]
        try:
            search = search_options[search_type](*args, **kwargs)

        except Exception as e:
            raise e

        return list(search)

    # INFO: Vulns
    def search_vulns(
        self,
        *severities: list[int],
        tool: TSCVulnTool = TSCVulnTool.VULNDETAILS,
        exploitable: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Retrieve the current vulnerabilities.

        Args:
            severities (List[str]): vuln severities to include
            tool (TSCVulnTool)    : tool to use for the search
            exploitable (bool)    : wheither to search only for exploitable vulnerabilities or not

        Returns:
            Dict : vulnerabilities matching arguments
        """

        filters: list[tuple[str, str, str]] = []

        if exploitable:
            filters.append(self.BUILTIN_FILTERS["exploitable"])

        filters.append(self.build_severity_filter(*severities))
        search = self.connection.analysis.vulns(*filters, tool=tool.value)

        return list(search)

    def build_severity_filter(
        self, *severities: list[int]
    ) -> tuple[Literal["severity"], Literal["="], str]:
        """
        Return a severity filter based on the provided severities.

        Args:
            severities (List[str]) : severities to include in the filter (see cve.py)
        """

        sev_scores = ",".join([f"{Severity.from_score(sev).score}" for sev in list(*severities)])
        return "severity", "=", sev_scores

    # INFO: Asset lists
    def create_asset_list(
        self,
        name: str,
        list_type: TSCAssetListType = TSCAssetListType.COMBINATION,
        description: str | None = None,
        ips: list[str] | None = None,
        dns_names: list[str] | None = None,
        *args: tuple,
        **kwargs: dict,
    ) -> None:
        """
        Create a new asset list.

        Args:
            name (str)                  : name of the asset list
            list_type (TSCAssetListType): type of the asset list (see tsc_asset_list_types.py for details)
            description (str)           : asset list description
            ips: (List[str])            : a list of ip addresses to associate with the list
            dns_names: (List[str])      : a list of dns names to associate with the list
            args (List)                 : list of additional arguments to pass to the new asset list
            kwargs (Dict)               : key-value couples to pass to the new asset list

        Raises:
            Exception: if something goes wrong while creating the asset list
        """

        self.check_connection()

        try:
            self.connection.asset_lists.create(
                name=name,
                description=description,
                list_type=list_type.value,
                ips=ips,
                dns_names=dns_names,
                *args,
                **kwargs,
            )

        except Exception as e:
            raise e

    def delete_asset_list(self, list_id: int | list[int]) -> None:
        """
        Delete an asset list based on given id.

        Args:
            list_id (int | List[int]) : list of ids of the asset lists to delete

        Raises:
            Exception: if something goes wrong while deleting the asset list
        """

        self.check_connection()

        if not isinstance(list_id, list):
            list_id = [list_id]

        try:
            for lid in list_id:
                self.connection.asset_lists.delete(id=lid)

        except Exception as e:
            raise e

    def list_asset_lists(
        self, list_filter: FilterTupleExtType | None = None
    ) -> list[dict[str, Any]]:
        """
        Retrieve a list of asset lists with minimal informations like list ids.

        Args:
            list_filter (Tuple[str, str, any]): filter to apply to the listing

        Returns:
            List[Dict]: asset lists matching filter

        Raises:
            Exception: if something goes wrong while listing asset lists
        """

        self.check_connection()

        asset_lists: list[dict[str, Any]] = []
        try:
            asset_lists_from_api: dict[str, Any] = self._connection.asset_lists.list()

            if asset_lists_from_api:
                asset_lists = asset_lists_from_api.get("usable", [])

            if list_filter:
                asset_lists = DataFilter.filter_data(
                    data_to_filter=asset_lists, filters=DataFilter.gen_from_tuple(list_filter)
                )

        except Exception as e:
            raise e

        return asset_lists

    def get_asset_list_details(self, list_id: int | list[int]) -> list[dict[str, Any]]:
        """
        Return the details of one or more asset lists.

        Args:
            list_id (int | List[int]): list of ids matching the asset lists to retrieve

        Returns:
            List[Dict]: list of asset list details

        Raises:
            Exception: if something goes wrong while reteiving asset list details
        """

        self.check_connection()

        if not isinstance(list_id, list):
            list_id = [list_id]

        list_details = []
        try:
            for lid in list_id:
                list_details.append(self.connection.asset_lists.details(id=lid))

        except Exception as e:
            raise e

        return list_details

    # TODO: Edit asset list
    # INFO: Scans
    def list_scans(self, scan_filter: FilterTupleExtType | None = None) -> list[dict[str, Any]]:
        """
        Retrieve a list of scans with minimal information like scan ids.

        Args:
            scan_filter (Tuple[str, str, any]) : filter to apply to the listing

        Return:
            List[Dict] : a list of scans matching the filter

        Raises:
            Exception: if something goes wrong while listing scans
        """

        self.check_connection()

        scan_list: list[dict[str, Any]] = []
        try:
            raw_scan_list: dict[str, Any] = self.connection.scans.list()

            if raw_scan_list is not None:
                scan_list = raw_scan_list.get("usable", [])

            if scan_filter:
                scan_list = DataFilter.filter_data(
                    data_to_filter=scan_list, filters=DataFilter.gen_from_tuple(scan_filter)
                )

        except Exception as e:
            raise e

        return scan_list

    def get_scan_details(self, scan_id: int | list[int]) -> list[dict[str, object]]:
        """
        Return the details of one or more scans.

        Args:
            scan_id (int | List[int]) : one or more scan id to retrieve

        Return:
            List[Dict] : a list of dicionaries containing scan details

        Raises:
            Exception: if something goes wrong while reteiving scan details
        """

        self.check_connection()

        if not isinstance(scan_id, list):
            scan_id = [scan_id]

        scan_details: list[dict[str, object]] = []
        try:
            for sid in scan_id:
                scan_details.append(self.connection.scans.details(id=sid))

        except Exception as e:
            raise e

        return scan_details

    def delete_scan(self, scan_id: int | list[int]) -> None:
        """
        Delete an asset list based on given id.

        Args:
            scan_id (int | List[int]) : one or more scan id to delete

        Raises:
            Exception: if something goes wrong while deleting scan
        """

        self.check_connection()

        if not isinstance(scan_id, list):
            scan_id = [scan_id]

        try:
            for sid in scan_id:
                self.connection.scans.delete(id=sid)

        except Exception as e:
            raise e

    def create_scan(
        self,
        name: str,
        repo_id: int,
        asset_lists: list[int] | None = None,
        description: str | None = None,
        schedule: dict[str, str] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Create a new scan.

        Args:
            name (str)             : name of the scan
            repo_id (int)          : repository id for the scan
            asset_lists (List[int]): the asset lists ids to run the scan against
            description (str)      : scan description
            schedule (Dict)        : schedule dictionary
            args (List)            : a list of additional arguments to pass to the new scan
            kwargs (Dict)          : key-value couples to pass to the new scan

        Raises:
            Exception: if something goes wrong while creating scan
        """

        self.check_connection()

        try:
            self.connection.scans.create(
                name=name,
                repo=repo_id,
                asset_lists=asset_lists,
                description=description,
                schedule=schedule,
                *args,
                **kwargs,
            )

        except Exception as e:
            raise e
