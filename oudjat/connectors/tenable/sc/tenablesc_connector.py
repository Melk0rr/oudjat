from typing import Dict
from tenable import sc

class TenabeSCConnector:
  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, url: str, access_key: str, secret_key: str):
    """ Constructor """
    
    self.api = sc.TenableSC(url, access_key=access_key, secret_key=secret_key)
    self.repos = self.api.repositories.list()
    

  def get_critical_vulns(self) -> Dict:
    """ Getter for current vulnerabilities """
    return self.api.analysis.vulns(('severity', '=', '4,3'),('exploitAvailable', '=', 'true'))