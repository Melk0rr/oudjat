import re
import json
import requests

from datetime import datetime
from typing import List, Dict, Union

from oudjat.utils.file import export_csv
from oudjat.utils.color_print import ColorPrint

CVE_REGEX = r'CVE-\d{4}-\d{4,7}'
CVRF_ID_REGEX = r'\d{4}-[a-zA-Z]{3}'
KB_NUM_REGEX = r'\d{7}'

API_REQ_HEADERS = { 'Accept': 'application/json' }
API_BASE_URL = "https://api.msrc.microsoft.com/"

def get_cvrf_id_from_cve(cve: str) -> str:
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
  

class MSAPIConnector:
  """ Connector to interact with Microsoft API """

  def __init__(self):
    """ Constructor """

    self.date = datetime.now()
    self.api_version = str(self.date.year)

    self.documents = {}

  def get_cve_knowledge_base(self, cve: str):
    """ Retreives CVE informations like KB, affected products, etc """
    cvrf_id = get_cvrf_id_from_cve(cve)

    cvrf = self.documents.get(cvrf_id, None)
    if cvrf is None:
      self.documents[cvrf_id] = CVRFDocument(cvrf_id)
      cvrf = self.documents[cvrf_id]

    cvrf.get_vulnerabilities()
    cve = cvrf.vulns[cve]
    print(cve.get_remediation_numbers())

  
class CVRFDocument:
  """ Class to manipulate MS CVRF documents """

  def __init__(self, id: str):
    """ Constructor """
    if not re.match(CVRF_ID_REGEX, id):
      raise ValueError(f"CVRF ID must follow the 'YYYY-MMM' format !")

    self.id = id
    self.url = f"{API_BASE_URL}cvrf/{self.id}"

    url_resp = requests.get(self.url, headers=API_REQ_HEADERS)
    
    if url_resp.status_code != 200:
      raise ConnectionError(f"Could not connect to {self.url}")
    
    self.content = json.loads(url_resp.content)
    self.products = None
    self.vulns = None

  def get_products(self) -> None:
    """ Retreives the products mentionned in the document """
    prods = {}
      
    prod_tree = self.content["ProductTree"]["Branch"][0]["Items"]
    for b in prod_tree:
      product_type = b["Name"]

      for p in b["Items"]:
        prods[p["ProductID"]] = MSProduct(id=p["ProductID"], name=p["Value"], type=b["Name"])

    self.products = prods
  
  def get_vulnerabilities(self) -> None:
    """ Retreives the vulnerabilities mentionned in the document """
    
    if self.products is None:
      self.get_products()

    vulns = {}
    
    for v in self.content["Vulnerability"]:
      vuln = MSAPIVuln(cve=v["CVE"])

      for kb in v["Remediations"]:
        kb_num = kb["Description"]["Value"]
        mskb = MSKB(num=kb_num)
        mskb.set_products([ self.products[id] for id in kb.get("ProductID", []) ])
        
        vuln.add_kb(kb_num=kb_num, kb=mskb)
        
      vulns[v["CVE"]] = vuln
      
    self.vulns = vulns

class MSAPIVuln:
  """ Class to manipulate CVE data related to MS products """

  def __init__(self, cve: str):
    """ Constructor """

    if not re.match(CVE_REGEX, cve):
      raise(f"Invalid CVE provided: {cve}")

    self.cve = cve
    self.kbs = {}
    self.products = {}
  
  def add_kb(self, kb_num: int, kb: "MSKB") -> None:
    """ Adds a KB to vuln KB list """
    if not re.match(KB_NUM_REGEX, kb_num):
      ColorPrint.yellow(f"Invalid KB number provided {kb_num}")
      return

    self.kbs[kb_num] = kb

  def get_cve(sefl) -> str:
    """ Getter for CVE """
    return self.cve
  
  def get_remediations(self) -> Dict[str, "MSKB"]:
    """ Getter for KB list """
    return self.kbs
  
  def get_remediation_numbers(self) -> List[int]:
    """ Returns kb numbers """
    return [ kb_number for kb_number in self.kbs.keys() ]

  def get_impacted_products(self) -> Dict[str, "MSProduct"]:
    """ Getter for impacted product list """
    return self.products
    
class MSProduct:
  """ Class to manipulate MS product """

  def __init__(self, id: str, name: str, type: str):
    """ Constructor """
    
    if not re.match(r'\d{4,5}(-\d{4,5})?', id):
      raise ValueError(f"Invalid MS product ID: {id}")

    self.pid = id
    self.name = name
    self.type = type
    self.subType = None
    
    if self.type == "ESU" or self.type == "Windows":
      self.subType = "Workstation"

      if "Server" in self.name:
        self.cptType = "Server"
        
  def to_string(self) -> str:
    """ Converts instance to string """
    return f"{self.pid}: {self.name}"

  def to_dict(self) -> Dict[str, str]:
    """ Converts instance to dict """
    return {
      "id": self.pid,
      "name": self.name,
      "type": self.type
    }

class MSKB:
  """ Class to manipulate MS KBs """

  def __init__(self, num: int):
    """ Constructor """
    self.number = num
    self.product_list = []
    self.cve_list = []
    
  def set_products(self, products: List["MSProduct"]) -> None:
    """ Setter for kb products """
    self.product_list = products

  def get_number(self) -> int:
    """ Getter for kb number """
    return self.number
    
  # def add_patched_cve(self, cve: str) -> None:
  #   """ Adds a CVE among the list of patched vulns """
  #   self.
