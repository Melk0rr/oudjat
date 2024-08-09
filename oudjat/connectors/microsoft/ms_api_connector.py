import re
import json
import requests

from datetime import datetime
from typing import List, Dict, Union, Any

from oudjat.utils.file import export_csv
from oudjat.utils.color_print import ColorPrint

from oudjat.connectors.connector import Connector
from oudjat.connectors.microsoft.ms_api_vars import API_BASE_URL, CVE_REGEX, API_REQ_HEADERS
from oudjat.connectors.microsoft.ms_cvrf_document import MSCVRFDocument


################################################################################
# MS API Connector class
class MSAPIConnector(Connector):
  """ Connector to interact with Microsoft API """

  def __init__(self):
    """ Constructor """

    self.date = datetime.now()
    self.api_version = str(self.date.year)

    super().__init__(target={}, service_name="OudjatMSAPI", use_credentials=False)
    self.connection = False

  def get_cvrf_id_from_cve(self, cve: str) -> str:
    """ Returns a CVRF ID based on a CVE ref """
    if not re.match(CVE_REGEX, cve):
      raise(f"Invalid CVE provided: {cve}")

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
    """ Retreives an existing document instance or create new one """
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
    """ Adds a CVRF document to the list """
    if doc.get_doc_id() not in self.target.keys():
      self.target[doc.get_doc_id()] = doc

  def search(
    self,
    search_filter: Union[str, List[str]],
  ) -> List[Dict]:
    """ Retreives CVE informations like KB, affected products, etc """
    res = []

    if not isinstance(search_filter, list):
      search_filter = [ search_filter ]

    for cve in search_filter:
      cvrf_id = self.get_cvrf_id_from_cve(cve)
      cvrf = self.connect(cvrf_id)
      
      if self.connection:
        cvrf.parse_vulnerabilities()

        cve = cvrf.get_vulnerabilities()[cve]
        res.append(cve)

    return res
