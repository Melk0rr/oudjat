import json
import requests

from datetime import datetime
from typing import List, Dict, Union

from oudjat.utils.file import export_csv
from oudjat.utils.color_print import ColorPrint

class MSAPIConnector:
  """ Connector to interact with Microsoft API """

  def __init__(self):
    """ Constructor """

    self.base_url = "https://api.msrc.microsoft.com/"
    self.cvrf_url = None
    self.headers = { 'Accept': 'application/json' }

    self.date = datetime.now()
    self.api_version = str(self.date.year)

  def get_cve_cvrf_id(self, cve: str):
    """ Returns the CVRF id for the given CVE """
    url = f"{self.base_url}Updates('{cve}')?api-version={self.api_version}"
    response = requests.get(url, headers=self.headers)

    cvrf_id = None
    if response.status_code == 200:
      data = json.loads(response.content)
      cvrf_id = data["value"][0]["ID"]

    return cvrf_id
    

  def get_cve_knoledge_base(self, cve: str):
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
