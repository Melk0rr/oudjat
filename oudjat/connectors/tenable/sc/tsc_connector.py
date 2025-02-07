import re

from urllib.parse import urlparse
from typing import Dict
from tenable.sc import TenableSC

from oudjat.utils import ColorPrint
from oudjat.connectors.connector import Connector


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

        self.repos = None

    def get_repos(self):
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

    def disconnect(self) -> None:
        """Disconnect from API"""
        del self.connection
        self.connection = None
        self.repos = None

    def get_critical_vulns(self) -> Dict:
        """Getter for current vulnerabilities"""
        if self.connection is None:
            raise ConnectionError("Connection not initialized")

        return self.connection.analysis.vulns(("severity", "=", "4,3"), ("exploitAvailable", "=", "true"))
