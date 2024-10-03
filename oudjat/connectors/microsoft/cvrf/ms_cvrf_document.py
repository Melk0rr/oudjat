import re
import json
import requests

from typing import Dict

from oudjat.utils import ColorPrint

from oudjat.connectors.microsoft import MSVuln
from oudjat.connectors.microsoft import MSRemed
from oudjat.connectors.microsoft import MSProduct
from oudjat.connectors.microsoft import API_BASE_URL, API_REQ_HEADERS, CVRF_ID_REGEX

class MSCVRFDocument:
  """ Class to manipulate MS CVRF documents """

  def __init__(self, id: str):
    """ Constructor """
    if not re.match(CVRF_ID_REGEX, id):
      raise ValueError("CVRF ID must follow the 'YYYY-MMM' format !")

    self.id = id
    self.url = f"{API_BASE_URL}cvrf/{self.id}"

    url_resp = requests.get(self.url, headers=API_REQ_HEADERS)
    
    if url_resp.status_code != 200:
      raise ConnectionError(f"Could not connect to {self.url}")
    
    ColorPrint.green(f"{self.url}")
    self.content = json.loads(url_resp.content)
    
    self.products = {}
    self.vulns = {}
    self.kbs = {}

  def get_doc_id(self) -> str:
    """ Getter for document id """
    return self.id

  def get_products(self) -> Dict[str, "MSProduct"]:
    """ Returns MS products mentionned in the document """
    if not self.products:
      self.parse_products()
    
    return self.products

  def get_vulnerabilities(self) -> Dict[str, "MSVuln"]:
    """ Returns vulnerabilities mentionned in the document """
    if not self.vulns:
      self.parse_vulnerabilities()
      
    return self.vulns
    
  def get_kbs(self) -> Dict[str, "MSRemed"]:
    """ Returns MS KBs mentionned in the document """
    if not self.kbs:
      self.parse_vulnerabilities()
      
    return self.kbs

  def add_product(self, product: "MSProduct") -> None:
    """ Adds a product to the list of the document products """
    if product.get_id() not in self.products.keys():
      self.products[product.get_id()] = product

  def add_vuln(self, vuln: "MSVuln") -> None:
    """ Adds a vuln to the list of the document vulnerabilities """
    if vuln.get_cve() not in self.vulns.keys():
      self.vulns[vuln.get_cve()] = vuln

  def add_kb(self, kb: "MSRemed") -> None:
    """ Adds a kb to the list of the kb mentionned in the document """
    if kb.get_number() not in self.kbs.keys():
      self.kbs[kb.get_number()] = kb

  def parse_products(self) -> None:
    """ Retreives the products mentionned in the document """
    prod_tree = self.content["ProductTree"]["Branch"][0]["Items"]
    for b in prod_tree:

      for p in b["Items"]:
        pid = p["ProductID"]
        prod = MSProduct(pid=pid, name=p["Value"], product_type=b["Name"])
        self.add_product(prod)

  def parse_vulnerabilities(self) -> None:
    """ Retreives the vulnerabilities mentionned in the document """
    
    if not self.products:
      self.parse_products()

    for v in self.content["Vulnerability"]:
      vuln = MSVuln(cve=v["CVE"])

      for kb in v["Remediations"]:
        kb_num = kb["Description"]["Value"]
        
        mskb = MSRemed(num=kb_num)
        mskb.set_products([ self.products[id] for id in kb.get("ProductID", []) ])

        self.add_kb(mskb)
        vuln.add_kb(kb_num=kb_num, kb=mskb)
        
      self.add_vuln(vuln)