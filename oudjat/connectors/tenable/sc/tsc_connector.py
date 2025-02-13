import re
from typing import List, Tuple
from urllib.parse import urlparse

from tenable.sc import TenableSC

from oudjat.connectors.connector import Connector
from oudjat.utils import ColorPrint

from .tsc_vuln import TenableSCVulns


class TenableSCConnector(Connector):
    # ****************************************************************
    # Attributes & Constructors

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
        self.vulns: TenableSCVulns = None

    # ****************************************************************
    # Methods

    def get_vulns(self) -> TenableSCVulns:
        """Returns a TenableSCVulns instance"""
        return self.vulns

    def get_repos(self) -> List:
        """Returns repositories list"""
        return self.repos

    def connect(self) -> None:
        """Connects to API using connector parameters"""
        connection = None
        try:
            connection = TenableSC(
                host=self.target.netloc,
                access_key=self.credentials.username,
                secret_key=self.credentials.password,
            )

        except Exception as e:
            raise e

        ColorPrint.green(f"Connected to {self.target.netloc}")
        self.connection = connection
        self.repos = self.connection.repositories.list()
        self.vulns = TenableSCVulns(tsc_connection=self.connection)

    def check_connection(self) -> None:
        """Checks if the connection is initialized"""
        if self.connection is None:
            raise ConnectionError("Connection not initialized")

    def disconnect(self) -> None:
        """Disconnect from API"""
        del self.connection
        self.connection = None
        self.repos = None

    def search(self, *search_filter: List[Tuple], search_type: str = "vulns") -> List:
        """Searches the API for elements"""
        self.check_connection()

        search_type = search_type.upper()
        search_options = {"VULNS": self.vulns.search}

        if search_type not in search_options.keys():
            raise ValueError(f"Invalid search type {search_type}")

        search = None
        try:
            search = search_options[search_type](search_filter)

        except Exception as e:
            raise e

        return list(search)

