import re
import json
import requests

from datetime import datetime
from typing import List, Dict, Union

from oudjat.utils.file import export_csv
from oudjat.utils.color_print import ColorPrint

CVE_REGEX = r'CVE-\d{4}-\d{4,7}'
API_REQ_HEADERS = { 'Accept': 'application/json' }

class MSAPIConnector:
  """ Connector to interact with Microsoft API """

  def __init__(self):
    """ Constructor """

    self.base_url = "https://api.msrc.microsoft.com/"

    self.date = datetime.now()
    self.api_version = str(self.date.year)

  def get_base_url(self) -> str:
    """ Getter for base URL """
    return self.base_url
  
  def get_api_version(self) -> str:
    """ Getter for api version """
    return self.api_version    

  def get_cve_knowledge_base(self, cve: str):
    """ Retreives CVE informations like KB, affected products, etc """
    cvrf_id = self.get_cve_cvrf_id(cve)

    headers = {'api-key': api_key, 'Accept': 'application/json'}
    response = requests.get(url, headers = headers)
    data = json.loads(response.content)

    for vuln in data["Vulnerability"]:
      if vuln["CVE"] == cve:
        print(vuln)
        

    kbs = {f"KB{kb['Description']['Value']}" for vuln in data["Vulnerability"] if vuln["CVE"] == cve for kb in vuln["Remediations"]}

    return kbs
  

class MSAPIVuln:
  """ Class to manipulate CVE data related to MS products """

  def __init__(self, cve: str, api_connector: "MSAPIConnector"):
    """ Constructor """

    if not re.match(CVE_REGEX, cve):
      throw(f"Invalid CVE provided: {cve}")

    self.api_connector = api_connector
    self.cve = cve

    self.id_url = self.api_connector.get_base_url()
    self.id_url += f"Updates('{cve}')?api-version={self.api_connector.get_api_version()}"

    self.cvrf_id = None

    # Retreive CVRF ID
    id_resp = requests.get(url, headers=API_REQ_HEADERS)
    if id_resp.status_code != 200
      throw ConnectionError(f"Could not connect to {self.id_url}")
      
    data = json.loads(id_resp.content)
    self.cvrf_id = data["value"][0]["ID"]


