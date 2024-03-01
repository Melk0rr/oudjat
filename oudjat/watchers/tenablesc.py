from tenable.sc import TenableSC
import json

class MySecurityCenter:
  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, url, access_key, secret_key):
    """ Constructor """
    
    self.api = TenableSC(url, access_key=access_key, secret_key=secret_key)
    self.repos = self.api.repositories.list()
    

  def get_critical_vulns(self):
    """ Getter for current vulnerabilities """
    return self.api.analysis.vulns(('severity', '=', '4,3'),('exploitAvailable', '=', 'true'))