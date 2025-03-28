import json
import re
from datetime import datetime
from typing import Dict, List, Union

import requests

from oudjat.connectors import Connector
from oudjat.utils import ColorPrint

from .definitions import API_BASE_URL, API_REQ_HEADERS, CVE_REGEX, MSCVRFDocument


class MSAPIConnector(Connector):
    """Connector to interact with Microsoft API"""

    # ****************************************************************
    # Attributes & Constructor

    def __init__(self):
        """Constructor"""

        self.date = datetime.now()
        self.api_version = str(self.date.year)

        super().__init__(target={}, service_name="OudjatMSAPI", use_credentials=False)
        self.connection = False

    # ****************************************************************
    # Methods

    def get_cvrf_id_from_cve(self, cve: str) -> str:
        """Returns a CVRF ID based on a CVE ref"""
        if not re.match(CVE_REGEX, cve):
            raise (f"Invalid CVE provided: {cve}")

        # API URL to retreive CVRF id from CVE
        id_url = f"{API_BASE_URL}Updates('{cve}')"

        cvrf_id = None

        # Retreive CVRF ID
        id_resp = requests.get(id_url, headers=API_REQ_HEADERS)
        if id_resp.status_code != 200:
            raise ConnectionError(f"Could not connect to {self.id_url}")

        data = json.loads(id_resp.content)
        cvrf_id = data["value"][0]["ID"]

        return cvrf_id

    def connect(self, cvrf_id: str) -> "MSCVRFDocument":
        """Retreives an existing document instance or create new one"""
        self.connection = False

        cvrf = self.target.get(cvrf_id, None)
        if cvrf is None:
            try:
                cvrf = MSCVRFDocument(cvrf_id)
                self.add_target(cvrf)
                self.connection = True

            except ConnectionError as e:
                ColorPrint.red(e)

        else:
            self.connection = True

        return self.target[cvrf_id]

    def add_target(self, doc: "MSCVRFDocument") -> None:
        """Adds a CVRF document to the list"""
        if doc.get_doc_id() not in self.target.keys():
            self.target[doc.get_doc_id()] = doc

    def search(
        self,
        search_filter: Union[str, List[str]],
    ) -> List[Dict]:
        """Retreives CVE informations like KB, affected products, etc"""
        res = []

        if not isinstance(search_filter, list):
            search_filter = [search_filter]

        for cve in search_filter:
            cvrf_id = self.get_cvrf_id_from_cve(cve)
            cvrf = self.connect(cvrf_id)

            if self.connection:
                cvrf.parse_vulnerabilities()
                res.append(cvrf.get_vulnerabilities()[cve])

        return res

