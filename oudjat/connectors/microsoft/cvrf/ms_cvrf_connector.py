"""Main module of the MS CVRF package that inits connection to a CVRF document."""

import json
import logging
import re
from datetime import datetime
from typing import override

from oudjat.connectors import Connector, ConnectorMethod
from oudjat.utils import Context, DataType
from oudjat.utils.types import StrType

from .definitions import API_BASE_URL, API_REQ_HEADERS, CVE_REGEX
from .ms_cvrf_document import MSCVRFDocument


class MSCVRFConnector(Connector):
    """Connector to interact with Microsoft API."""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(self) -> None:
        """
        Initialize a new instance of MSAPIConnector.

        This method sets up the connector by initializing the current date and version,
        setting up the connection using superclass methods, and marking it as not connected.
        """

        self.logger: "logging.Logger" = logging.getLogger(__class__.__name__)

        self._date: datetime = datetime.now()
        self._api_version: str = str(self._date.year)

        super().__init__(target={})
        self._connection: bool = False

    # ****************************************************************
    # Methods

    def _cvrf_id_from_cve(self, cve: str) -> str:
        """
        Retrieve a CVRF ID based on a provided CVE reference.

        Args:
            cve (str): The CVE identifier to search for.

        Returns:
            str: The CVRF ID corresponding to the given CVE.

        Raises:
            ValueError     : If the provided CVE is invalid.
            ConnectionError: If unable to connect to the API to retrieve the CVRF ID.
        """

        context = Context()
        if not re.match(CVE_REGEX, cve):
            raise ValueError(f"{context}::Invalid CVE provided: {cve}")

        # API URL to retrieve CVRF id from CVE
        id_url = f"{API_BASE_URL}Updates('{cve}')"

        # Retrieve CVRF ID
        id_resp = ConnectorMethod.GET(id_url, headers=API_REQ_HEADERS)
        if id_resp.status_code != 200:
            raise ConnectionError(f"{context}::Could not connect to {id_url}")

        data = json.loads(id_resp.content)
        return data["value"][0]["ID"]

    @override
    def connect(self, cvrf_id: str) -> None:
        """
        Retrieve an existing document instance or creates a new one based on the CVRF ID.

        Args:
            cvrf_id (str): The identifier of the CVRF document to connect to.

        Returns:
            MSCVRFDocument: An instance of the CVRF document corresponding to the provided CVRF ID.
        """

        context = Context()
        self.logger.info(f"{context}::Connecting to {cvrf_id}")

        self._connection = False

        cvrf = self._target.get(cvrf_id, None)
        if cvrf is None:
            try:
                cvrf = MSCVRFDocument(cvrf_id)
                self.add_target(cvrf)
                self._connection = True

                self.logger.info(f"{context}::Connected to {cvrf_id}")

            except ConnectionError as e:
                self.logger.error(
                    f"{context}.connect::Could not connect to the provided CVRF document {e}"
                )

        else:
            self._connection = True

    def add_target(self, doc: "MSCVRFDocument") -> None:
        """
        Add a CVRF document to the internal target dictionary.

        Args:
            doc (MSCVRFDocument): The CVRF document instance to be added.
        """

        if doc.id not in self._target.keys():
            self._target[doc.id] = doc

    @override
    def fetch(
        self,
        search_filter: StrType,
    ) -> "DataType":
        """
        Search for information about CVEs based on the provided filter.

        Args:
            search_filter (str | list[str]): The CVE identifier or list of identifiers to search for.

        Returns:
            DataType: A list of dictionaries containing vulnerability information corresponding to the filtered CVEs.
        """

        context = Context()
        res = []

        if not isinstance(search_filter, list):
            search_filter = [search_filter]

        for cve in search_filter:
            cvrf_id = self._cvrf_id_from_cve(cve)

            self.logger.debug(f"{context}::{cvrf_id}")
            _ = self.connect(cvrf_id)
            cvrf: "MSCVRFDocument" = self._target.get(cvrf_id, None)

            if self._connection:
                self.logger.debug(f"{context}::{cvrf_id} > {cvrf.to_dict()}")

                cvrf.parse_vulnerabilities()
                res.append(cvrf.vulnerabilities[cve])

        return res
