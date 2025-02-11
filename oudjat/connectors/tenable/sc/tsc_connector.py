import re
from enum import Enum
from typing import Dict, List, Tuple, Union
from urllib.parse import urlparse

from tenable.sc import TenableSC

from oudjat.connectors.connector import Connector
from oudjat.utils import ColorPrint


class TenableSCSeverity(Enum):
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    INFO = 0


class TenableSCConnector(Connector):
    # ****************************************************************
    # Attributes & Constructors

    BUILTIN_FILTERS = {
        "exploitable": ("exploitAvailable", "=", "true")
    }

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

        self.reset_vulns()

    def get_vuln_number(self, *severities: List[str]) -> int:
        """Returns a number of vulnerabilities currently retreived based on the provided severities"""
        if severities is None:
            severities = TenableSCSeverity._member_names_

        count = 0
        for sev in severities:
            if sev.upper() in TenableSCSeverity._member_names_:
                count += len(self.vulns[sev.upper()])

        return count

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

    def check_connection(self) -> None:
        """Checks if the connection is initialized"""
        if self.connection is None:
            raise ConnectionError("Connection not initialized")

    def disconnect(self) -> None:
        """Disconnect from API"""
        del self.connection
        self.connection = None
        self.repos = None

    def reset_vulns(self, *severities: List[str]) -> None:
        """Resets vulns list"""
        if severities is None:
            severities = TenableSCSeverity._member_names_

        for sev in severities:
            if sev.upper() in TenableSCSeverity._member_names_:
                self.vulns[sev.upper()].clear()

    def search(self, *search_filter: List[Tuple], search_type: str = "vulns") -> List:
        """Searches the API for elements"""
        self.check_connection()

        search_type = search_type.upper()
        search_options = {"VULNS": self.connection.analysis.vulns}

        if search_type not in search_options.keys():
            raise ValueError(f"Invalid search type {search_type}")

        search = None
        try:
            search = search_options[search_type](search_filter)

        except Exception as e:
            raise e

        return list(search)

    def search_vulns(self, *search_filter: List[Tuple]) -> List:
        """Searches for vulns"""
        return self.search(search_filter=search_filter)

    def add_vuln(self, vuln: Union[Dict, List[Dict]]) -> None:
        """Adds a vuln to the connector vuln dictionary"""
        if not isinstance(vuln, list):
            vuln = [vuln]

        for v in vuln:
            self.vulns[v["severity"]["name"].upper()] = v

    def build_severity_filter(self, *severities: List[str]) -> Tuple:
        """Returns a severity filter based on the provided severities"""
        return ("severity", "=", ','.join([ TenableSCSeverity[sev] for sev in severities ]))

    def get_vulns(self, *severities: List[str]) -> Dict:
        """Getter for the currently retreived vulnerabilities"""
        if self.connection is None:
            return None

        filters = [ self.BUILTIN_FILTERS["exploitable"] ]
        if severities is not None:
            filters += self.build_severity_filter(severities)

        if self.get_vuln_number() == 0:
            exploitable_vulns = self.search_vulns(*filters)
            self.add_vuln(exploitable_vulns)

        return { key: self.vulns[key] for key in severities }

