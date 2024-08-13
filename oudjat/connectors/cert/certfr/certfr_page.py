import re
import requests

from typing import List, Dict, Set, Union
from bs4 import BeautifulSoup, element

from oudjat.utils.color_print import ColorPrint
from oudjat.model.cve import CVE, CVE_REGEX
from oudjat.connectors.cert.risk_types import RiskTypes
from oudjat.connectors.cert.certfr.certfr_page_types import CERTFRPageTypes
from oudjat.connectors.cert.certfr.certfr_page_meta import CERTFRPageMeta
from oudjat.connectors.cert.certfr.certfr_page_content import CERTFRPageContent

REF_TYPES = '|'.join([ pt.name for pt in CERTFRPageTypes ])
LINK_TYPES = '|'.join([ pt.value for pt in CERTFRPageTypes ])
CERTFR_REF_REGEX = rf"CERTFR-\d{{4}}-(?:{REF_TYPES})-\d{{3,4}}"
CERTFR_LINK_REGEX = rf"https:\/\/www\.cert\.ssi\.gouv\.fr\/(?:{LINK_TYPES})\/{CERTFR_REF_REGEX}"
URL_REGEX = r'http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

class CERTFRPage:
  """ Describes a CERTFR page """

  # ****************************************************************
  # Attributes & Constructors

  BASE_LINK = "https://www.cert.ssi.gouv.fr"

  def __init__(self, ref: str):
    """ Constructor """

    if not self.is_valid_ref(ref) and not self.is_valid_link(ref):
      raise ValueError(f"Invalid CERTFR ref provided : {ref}")
    
    self.ref = ref if self.is_valid_ref(ref) else self.get_ref_from_link(ref)

    self.raw_content = None
    self.title: str = None

    self.meta = None
    self.content = None

    # Set page type
    ref_type = re.search(rf"(?:{REF_TYPES})", self.ref).group(0)
    self.page_type = CERTFRPageTypes[ref_type].value
    
    self.link = f"{self.BASE_LINK}/{self.page_type}/{self.ref}/"

  # ****************************************************************
  # Methods

  def get_ref(self) -> str:
    """ Getter for the reference """
    return self.ref

  def get_max_cve(self, cve_data: List["CVE"] = None) -> Union["CVE", List["CVE"]]:
    """ Returns the highest cve """
    if len(self.content.get_cves()) == 0:
      print("No comparison possible: no CVE related")
      return None
    
    print(f"\nResolving most critical CVE for {self.ref}")

    if not self.CVE_RESOLVED:
      self.resolve_cve_data(cve_data)

    max_cve = max(self.cves, key=lambda cve: cve.get_cvss())
    self.documentations.append(max_cve.get_link())
    print(f"\n{self.ref} max CVE is {max_cve.get_ref()}({max_cve.get_cvss()})")

    return max_cve

  def connect(self) -> None:
    """ Connects to a CERTFR page based on given ref """
     # Handle possible connection error
    try:
      req = requests.get(self.link)
      
      if req.status_code != 200:
        raise ConnectionError(f"Error while trying to connect to self.target")
      
      self.raw_content = BeautifulSoup(req.content, 'html.parser')
      self.title = self.raw_content.title.text

    except ConnectionError:
      ColorPrint.red(
        f"CERTFRPage::Error while requesting {self.ref}. Make sure it is accessible")

  def disconnect(self) -> None:
    """ Resets parsing """
    self.raw_content = None
    self.meta = None
    self.content = None

  def parse(self) -> None:
    """ Parse page content """
    
    if self.raw_content is None:
      self.connect()
      
    try:
      sections = self.raw_content.article.find_all("section")

      # Meta parsing
      self.meta = CERTFRPageMeta(meta_section=sections[0], page=self)
      self.meta.parse()

      # Content parsing
      self.content = CERTFRPageContent(content_section=sections[1], page=self)
      self.content.parse()

    except Exception as e:
      ColorPrint.red(
          f"CERTFRPage::A parsing error occured for {self.ref}\n{e}")

  def to_string(self) -> str:
    """ Converts current instance into a string """
    return f"{self.ref}: {self.title}"

  def to_dictionary(self) -> Dict:
    """ Converts current instance into a dictionary """
    return {
      "ref": self.ref,
      "title": self.title,
      "date_initial": self.date_initial,
      "date_last": self.date_last,
      "sources": self.sources,
      "cve": self.get_cve_refs(),
      "risks": self.get_risks(),
      "products": self.affected_products,
      "docs": self.get_documentations(filter="cve.org"),
      "link": self.target
    }

  def resolve_cve_data(self, cve_data: List["CVE"]) -> None:
    """ Resolves CVE data for all related CVE """
    print(f"\nResolving {len(self.cves)} CVE data for {self.ref}...")

    for cve in self.cves:
      # Checks if the current CVE can be found in the provided cve list. If not : parse Nist page
      cve_imported = False
      if cve_data:
        cve_search = CVE.find_cve_by_ref(ref=cve.get_ref(), cve_list=cve_data)
        
        if cve_search:
          print(f"Found {cve.get_ref()} in CVE list ! Copying data...")
          cve.copy(cve_search)
          cve_imported = True

      if not cve_imported:
        cve.parse_nist(verbose=False)

    self.CVE_RESOLVED = True

  # ****************************************************************
  # Static methods

  @staticmethod
  def is_valid_ref(ref: str) -> bool:
    """ Returns whether the ref is valid or not """
    return re.match(CERTFR_REF_REGEX, ref)

  @staticmethod
  def is_valid_link(link: str) -> bool:
    """ Returns whether the link is valid or not """
    return re.match(CERTFR_LINK_REGEX, link)

  @staticmethod
  def get_ref_from_link(link: str) -> str:
    """ Returns a CERTFR ref based on a link """
    if not re.match(CERTFR_LINK_REGEX, link):
      raise ValueError(f"Invalid CERTFR link provided: {link}")

    return re.findall(CERTFR_REF_REGEX, link)[0]