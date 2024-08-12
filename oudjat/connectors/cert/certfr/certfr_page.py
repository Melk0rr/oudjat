import re
import requests

from typing import List, Dict, Set, Union
from bs4 import BeautifulSoup, element

from oudjat.utils.color_print import ColorPrint
from oudjat.connectors.cert.risk_types import RiskTypes
from oudjat.connectors.cert.certfr.certfr_page_types import CERTFRPageTypes

REF_TYPES = '|'.join([ pt.name for pt in CERTFRPageTypes ])
LINK_TYPES = '|'.join([ pt.value for pt in CERTFRPageTypes ])
CERTFR_REF_REGEX = rf"CERTFR-\d{{4}}-(?:{REF_TYPES})-\d{{3,4}}"
CERTFR_LINK_REGEX = rf"https:\/\/www\.cert\.ssi\.gouv\.fr\/(?:{LINK_TYPES})\/{CERTFR_REF_REGEX}"
URL_REGEX = r'http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

class CERTFRPage:

  # ****************************************************************
  # Attributes & Constructors

  BASE_LINK = "https://www.cert.ssi.gouv.fr"

  def __init__(self, ref: str):
    """ Constructor """

    if not self.is_valid_ref(ref) and not self.is_valid_link(ref):
      raise ValueError(f"Invalid CERTFR ref provided : {ref}")
    
    self.ref = ref if self.is_valid_ref(ref) else self.get_ref_from_link(ref)

    self.raw_content = None
    self.meta = None
    self.content = None

    self.title: str = None
    self.date_initial: str = None
    self.date_last: str = None
    self.cve_list: Set["CVE"] = set()
    self.risks: Set[str] = set()
    self.sources: List[str] = []
    self.documentations: List[str] = []
    self.affected_products: List[str] = []

    # Set page type
    ref_type = re.search(rf"(?:{REF_TYPES})", self.ref).group(0)
    self.page_type = CERTFRPageTypes[ref_type].value
    
    self.link = f"{self.BASE_LINK}/{self.page_type}/{self.ref}/"

  # ****************************************************************
  # Methods

  def get_ref(self) -> str:
    """ Getter for the reference """
    return self.ref

  def get_date_initial(self) -> str:
    """ Getter / parser for initial page date """
    if self.meta is None:
      return None
    
    if self.date_initial is None:
      self.date_initial = self.meta.get("Date de la première version", None)

    return self.date_initial

  def get_date_last(self) -> str:
    """ Getter / parser for page last change date """
    if self.meta is None:
      return None
    
    if self.date_last is None:
      self.date_last = self.meta.get("Date de la dernière version", None)

    return self.date_last

  def get_sources(self) -> List[str]:
    """ Getter / parser for page sources """

    if self.meta is None:
      return []
    
    if len(self.sources) == 0:
      clean_sources = self.meta.get("Source(s)", "").split("\n")
      clean_sources = [
        re.sub(r'\s+', ' ', line).strip()
        for line in clean_sources if re.sub(r'\s+', '', line).strip()
      ]

      self.sources = clean_sources

    return self.sources

  def get_risks(self, short: bool = True) -> List[str]:
    """ Get the list of risks """
    return [ r.name if short else r.value for r in self.risks ]

  def get_cve_refs(self) -> List[str]:
    """ Returns the refs of all the related cves """
    return [ cve.get_ref() for cve in self.cve_list ]

  def get_max_cve(self, cve_data: List["CVE"] = None) -> "CVE":
    """ Returns the highest cve """
    if len(self.cve_list) <= 0:
      print("No comparison possible: no CVE related")
      return None
    
    print(f"\nResolving most critical CVE for {self.ref}")

    if not self.CVE_RESOLVED:
      self.resolve_cve_data(cve_data)

    max_cve = max(self.cve_list, key=lambda cve: cve.get_cvss())
    self.documentations.append(max_cve.get_link())
    print(f"\n{self.ref} max CVE is {max_cve.get_ref()}({max_cve.get_cvss()})")

    return max_cve

  def get_documentations(self, filter: str = None) -> List[str]:
    """ Getter for the documentations """
    docs = self.documentations

    if filter is not None and filter != "":
      docs = [ d for d in self.documentations if filter not in d ]

    return docs

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
        f"Error while requesting {self.ref}. Make sure it is accessible")

  def disconnect(self) -> None:
    """ Resets parsing """
    self.raw_content = None
    self.meta = None
    self.content = None

    self.title: str = None
    self.date_initial: str = None
    self.date_last: str = None
    self.cve_list: Set["CVE"] = set()
    self.risks: Set[str] = set()
    self.sources: List[str] = []
    self.documentations: List[str] = []
    self.affected_products: List[str] = []

  def parse_meta(self) -> None:
    """ Parse meta table """
    self.sections["meta"].find_all("table")[0]
    meta = {}

    for row in meta_tab.find_all("tr"):
      cells = row.find_all("td")
      c_name = cells[0].text.strip()
      c_value = cells[-1].text.strip()

      meta[self.clean_str(c_name)] = self.clean_str(c_value)
      
    self.meta = meta

  def parse_list_from_title(self, title: str, h_level: str = "h1") -> Union[str, List[str]]:
    """ Parse a list located next to given title """
    title = self.content.find_all(h_level, string=title)[0]
    ul = title.find_next("ul")
    return [ e.text for e in ul.find_all("li") ]

  def parse_text_from_title(self, title: str, h_level: str = "h1") -> Union[str, List[str]]:
    """ Parse a paragraph located next to given title """
    title = self.content.find_all(h_level, string=title)
    return title.find_next("p").text

  def parse_content(self) -> None:
    """ Parse content section """
    content = {}
    
    # Risks
    content["risks"] = self.parse_list_from_title("Risques", h_level="h2")
    
    # Products
    content["products"] = self.parse_list_from_title(title="Systèmes affectés", h_level="h2")
    
    # Description
    content["description"] = self.parse_text_from_title(title="Résumé", h_level="h2")
    
    # Solutions
    content["solutions"] = self.parse_text_from_title(title="Solutions", h_level="h2")
    
    # Documentations
    content["documentations"] = re.findall(URL_REGEX, self.content.text)

  def parse(self) -> None:
    """ Parse page content """
    
    if self.raw_content is None:
      self.connect()
      
    try:
      sections = self.raw_content.article.find_all("section")

      # Meta parsing
      self.meta = sections[0].find_all("table")[0]
      self.parse_meta()

      self.get_date_initial()
      self.get_date_last()
      self.get_sources()

      # Content parsing
      self.content = sections[1]
      self.parse_content()

    except Exception as e:
      ColorPrint.red(
          f"A parsing error occured for {self.ref}: {e}\nCheck if the page has the expected format.")

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
    print(f"\nResolving {len(self.cve_list)} CVE data for {self.ref}...")

    for cve in self.cve_list:
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
  def clean_str(str: str) -> str:
    return str.replace("\r", "").strip()

  @staticmethod
  def get_ref_from_link(link: str) -> str:
    """ Returns a CERTFR ref based on a link """
    if not re.match(CERTFR_LINK_REGEX, link):
      raise ValueError(f"Invalid CERTFR link provided: {link}")

    return re.findall(CERTFR_REF_REGEX, link)[0]