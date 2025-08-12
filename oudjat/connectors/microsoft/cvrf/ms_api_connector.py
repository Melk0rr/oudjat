"""Main module of the MS CVRF package that inits connection to a CVRF document."""

import json
import re
from datetime import datetime
from typing import Any, override

import requests

from oudjat.connectors import Connector
from oudjat.utils import ColorPrint
from oudjat.utils.types import StrType

from .definitions import API_BASE_URL, API_REQ_HEADERS, CVE_REGEX
from .ms_cvrf_document import MSCVRFDocument


class MSCVRFConnector(Connector):
    """Connector to interact with Microsoft API."""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(self):
        """
        Initialize a new instance of MSAPIConnector.

        This method sets up the connector by initializing the current date and version,
        setting up the connection using superclass methods, and marking it as not connected.
        """

        self._date: datetime = datetime.now()
        self._api_version: str = str(self._date.year)

        super().__init__(target={}, service_name="OudjatMSAPI", use_credentials=False)
        self._connection: bool = False

    # ****************************************************************
    # Methods

    def get_cvrf_id_from_cve(self, cve: str) -> str:
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

        if not re.match(CVE_REGEX, cve):
            raise ValueError(f"{__class__.__name__}.get_cvrf_id_from_cve::Invalid CVE provided: {cve}")

        # API URL to retrieve CVRF id from CVE
        id_url = f"{API_BASE_URL}Updates('{cve}')"

        cvrf_id = None

        # Retrieve CVRF ID
        id_resp = requests.get(id_url, headers=API_REQ_HEADERS)
        if id_resp.status_code != 200:
            raise ConnectionError(
                f"{__class__.__name__}.get_cvrf_id_from_cve::Could not connect to {id_url}"
            )

        data = json.loads(id_resp.content)
        cvrf_id = data["value"][0]["ID"]

        return cvrf_id

    @override
    def connect(self, cvrf_id: str) -> None:
        """
        Retrieve an existing document instance or creates a new one based on the CVRF ID.

        Args:
            cvrf_id (str): The identifier of the CVRF document to connect to.

        Returns:
            MSCVRFDocument: An instance of the CVRF document corresponding to the provided CVRF ID.
        """

        self._connection = False

        cvrf = self._target.get(cvrf_id, None)
        if cvrf is None:
            try:
                cvrf = MSCVRFDocument(cvrf_id)
                self.add_target(cvrf)
                self._connection = True

            except ConnectionError as e:
                ColorPrint.red(f"{__class__.__name__}.connect::Could not connect to the provided CVRF document {e}")

        else:
            self._connection = True

    def add_target(self, doc: "MSCVRFDocument") -> None:
        """
        Add a CVRF document to the internal target dictionary.

        Args:
            doc (MSCVRFDocument): The CVRF document instance to be added.
        """

        if doc.get_doc_id() not in self._target.keys():
            self._target[doc.get_doc_id()] = doc

    @override
    def search(
        self,
        search_filter: StrType,
    ) -> list[dict[str, Any]]:
        """
        Search for information about CVEs based on the provided filter.

        Args:
            search_filter (Union[str, List[str]]): The CVE identifier or list of identifiers to search for.

        Returns:
            List[Dict]: A list of dictionaries containing vulnerability information corresponding to the filtered CVEs.
        """

        res = []

        if not isinstance(search_filter, list):
            search_filter = [search_filter]

        for cve in search_filter:
            cvrf_id = self.get_cvrf_id_from_cve(cve)
            _ = self.connect(cvrf_id)
            cvrf = self._target.get(cvrf_id, None)

            if self.connection:
                cvrf.parse_vulnerabilities()
                res.append(cvrf.get_vulnerabilities()[cve])

        return res

