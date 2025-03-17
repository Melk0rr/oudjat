import re
from typing import Any, Dict, List, Tuple, Union
from urllib.parse import urlparse

from tenable.sc import TenableSC

from oudjat.connectors.connector import Connector
from oudjat.control.data.data_filter_operations import DataFilterOperation
from oudjat.model.vulnerability.cve import get_severity_by_score
from oudjat.utils import ColorPrint

from .tsc_asset_list_types import TSCAssetListType


class TenableSCConnector(Connector):
    # ****************************************************************
    # Attributes & Constructors

    BUILTIN_FILTERS = {"exploitable": ("exploitAvailable", "=", "true")}

    def __init__(
        self, target: str, service_name: str = "OudjatTenableSCAPI", port: int = 443
    ) -> None:
        """Constructor"""

        scheme = "http"
        if port == 443:
            scheme += "s"

        if not re.match(r"http(s?):", target):
            target = f"{scheme}://{target}"

        super().__init__(target=urlparse(target), service_name=service_name, use_credentials=True)
        self.target = urlparse(f"{self.target.scheme}://{self.target.netloc}")
        self.connection: TenableSC = None
        self.repos = None

    # ****************************************************************
    # Methods

    # INFO: Getters
    def get_repos(self) -> List:
        """Returns repositories list"""
        return self.repos

    # INFO: Base connector methods
    def connect(self) -> None:
        """Connects to API using connector parameters"""
        connection = None
        try:
            connection = TenableSC(
                host=self.target.netloc,
                access_key=self.credentials.username,
                secret_key=self.credentials.password,
            )

            ColorPrint.green(f"Connected to {self.target.netloc}")
            self.connection = connection
            self.repos = self.connection.repositories.list()

        except Exception as e:
            raise e

    def check_connection(self, prefix: str = None) -> None:
        """Checks if the connection is initialized"""

        if self.connection is None:
            error_pre = '.' + prefix if prefix is not None else ''
            error_msg = f"TenableSCConnector{error_pre}::Can't create asset list if connection is not initialized"
            raise ConnectionError(error_msg)

    def disconnect(self) -> None:
        """Disconnect from API"""
        del self.connection
        self.connection = None
        self.repos = None

    def search(self, search_type: str, *args, **kwargs) -> List:
        """Searches the API for elements"""

        self.check_connection(prefix="search")

        search_type = search_type.upper()
        search_options = {"VULNS": self.search_vulns}

        if search_type not in search_options.keys():
            raise ValueError(f"Invalid search type {search_type}")

        search = None
        try:
            search = search_options[search_type](*args, **kwargs)

        except Exception as e:
            raise e

        return list(search)

        """Raises an exception if connection is not set"""

    # INFO: Vulns
    def search_vulns(
        self, *severities: List[str], key_exclude: List[str] = None, tool: str = "vulndetails"
    ) -> Dict:
        """Retrieve the current vulnerabilities"""

        filters = [self.BUILTIN_FILTERS["exploitable"]]
        if severities is not None:
            filters.append(self.build_severity_filter(severities))

        search = self.connection.analysis.vulns(*filters, tool=tool)
        return list(search)

    def build_severity_filter(self, *severities: List[str]) -> Tuple:
        """Returns a severity filter based on the provided severities"""
        sev_scores = ",".join(
            [f"{get_severity_by_score(sev).value['score']}" for sev in list(*severities)]
        )
        return "severity", "=", sev_scores

    # INFO: Asset lists
    def create_asset_list(
        self,
        name: str,
        list_type: TSCAssetListType = TSCAssetListType.COMBINATION,
        description: str = None,
        ips: List[str] = None,
        dns_names: List[str] = None,
    ) -> None:
        """Creates a new asset list"""

        self.check_connection(prefix="create_asset_list")

        try:
            self.connection.asset_lists.create(
                name=name,
                description=description,
                list_type=list_type.value,
                ips=ips,
                dns_names=dns_names,
            )

        except Exception as e:
            raise e

    def delete_asset_list(self, list_id: Union[int, List[int]]) -> None:
        """Deletes an asset list based on given id"""

        self.check_connection(prefix="delete_asset_list")

        if not isinstance(list_id, list):
            list_id = [list_id]

        try:
            for lid in list_id:
                self.connection.asset_lists.delete(id=lid)

        except Exception as e:
            raise e

    def list_asset_lists(self, list_filter: Tuple[str, str, Any] = None) -> List[Dict]:
        """Retrieves a list of asset lists"""

        self.check_connection(prefix="list_asset_lists")

        asset_lists = []
        try:
            asset_lists = self.connection.asset_lists.list()

            if asset_lists is not None:
                asset_lists = asset_lists.get("usable", [])

            # If a filter is provided
            if list_filter is not None:
                f_key, f_operator, f_value = list_filter
                asset_lists = list(
                    filter(
                        lambda al: DataFilterOperation[f_operator](f_value, al[f_key]), asset_lists
                    )
                )

        except Exception as e:
            raise e

        return asset_lists

    def get_asset_list_details(self, list_id: Union[int, List[int]]) -> List[Dict]:
        """Returns the details of one or more asset lists"""

        self.check_connection(prefix="get_asset_list_details")

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
    def list_scans(self, scan_filter: Tuple[str, str, Any] = None) -> List[Dict]:
        """Retrieves a list of scans"""

        self.check_connection(prefix="list_scans")

        scan_list = []
        try:
            scan_list = self.connection.scans.list()

            if scan_list is not None:
                scan_list = scan_list.get("usable", [])

            # If a filter is provided
            if scan_filter is not None:
                f_key, f_operator, f_value = scan_filter
                scan_list = list(
                    filter(
                        lambda sl: DataFilterOperation[f_operator](f_value, sl[f_key]), scan_list
                    )
                )

        except Exception as e:
            raise e

        return scan_list

    # TODO: Get scans details
    def get_scan_details(self, scan_id: Union[int, List[int]]) -> List[Dict]:
        """Returns the details of one or more scans"""

        self.check_connection(prefix="get_scan_details")

        if not isinstance(scan_id, list):
            scan_id = [scan_id]

        scan_details = []
        try:
            for sid in scan_id:
                scan_details.append(self.connection.scans.details(id=sid))

        except Exception as e:
            raise e

        return scan_details

    # TODO: Delete scans details
    # TODO: Create scans details
