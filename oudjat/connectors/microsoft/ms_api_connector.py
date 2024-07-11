import re
import json
import requests

from datetime import datetime
from typing import List, Dict, Union

from oudjat.utils.file import export_csv
from oudjat.utils.color_print import ColorPrint

CVE_REGEX = r'CVE-\d{4}-\d{4,7}'
API_REQ_HEADERS = { 'Accept': 'application/json' }
API_BASE_URL = "https://api.msrc.microsoft.com/"

class MSAPIConnector:
  """ Connector to interact with Microsoft API """

  def __init__(self):
    """ Constructor """

    self.

    self.date = datetime.now()
    self.api_version = str(self.date.year)
  
  def get_api_version(self) -> str:
    """ Getter for api version """
    return self.api_version    

  def get_cve_knowledge_base(self, cve: str):
    """ Retreives CVE informations like KB, affected products, etc """
    vuln = MSAPIVuln(cve, self)

    # headers = {'api-key': api_key, 'Accept': 'application/json'}
    # response = requests.get(url, headers = headers)
    # data = json.loads(response.content)

    # for vuln in data["Vulnerability"]:
    #   if vuln["CVE"] == cve:
    #     print(vuln)
        

    # kbs = {f"KB{kb['Description']['Value']}" for vuln in data["Vulnerability"] if vuln["CVE"] == cve for kb in vuln["Remediations"]}

    # return kbs
  

class MSAPIVuln:
  """ Class to manipulate CVE data related to MS products """

  def __init__(self, cve: str, api_connector: "MSAPIConnector"):
    """ Constructor """

    if not re.match(CVE_REGEX, cve):
      raise(f"Invalid CVE provided: {cve}")

    self.api_connector = api_connector
    self.cve = cve

    # API URL to retreive CVRF id from CVE
    id_url = f"{API_BASE_URL}Updates('{cve}')?api-version={self.api_connector.get_api_version()}"

    self.cvrf_id = None

    # Retreive CVRF ID
    id_resp = requests.get(id_url, headers=API_REQ_HEADERS)
    if id_resp.status_code != 200:
      raise ConnectionError(f"Could not connect to {self.id_url}")
      
    data = json.loads(id_resp.content)
    self.cvrf_id = data["value"][0]["ID"]
    
    self.cvrf_document = None
    self.products = {}
    
  def get_cvrf_document(self) -> None:
    """ Get the CVRF document from  """
    cvrf_url = f"{API_BASE_URL}cvrf/{cvrf_id}?api-version={self.api_connector.get_api_version()}"

    cvrf_resp = requests.get(cvrf_url, headers=API_REQ_HEADERS)
    data = json.loads(cvrf_resp)
    
    self.cvrf_document = data



