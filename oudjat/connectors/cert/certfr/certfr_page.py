import re
import requests

from typing import List, Dict, Set
from bs4 import BeautifulSoup, element

from oudjat.utils.color_print import ColorPrint
from oudjat.model.vulnerability.cve import CVE, CVE_REGEX
from oudjat.connectors.cert.risk_types import RiskType
from oudjat.connectors.cert.certfr.certfr_page_types import CERTFRPageType

REF_TYPES = '|'.join([ pt.name for pt in CERTFRPageType ])
LINK_TYPES = '|'.join([ pt.value for pt in CERTFRPageType ])
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

    self.raw_content: element = None
    self.title: str = None

    self.meta: CERTFRPageMeta = None
    self.content: CERTFRPageContent = None

    self.CVE_RESOLVED = False

    # Set page type
    ref_type = re.search(rf"(?:{REF_TYPES})", self.ref).group(0)
    self.page_type = CERTFRPageType[ref_type].value
    
    self.link = f"{self.BASE_LINK}/{self.page_type}/{self.ref}/"

  # ****************************************************************
  # Methods

  def get_ref(self) -> str:
    """ Getter for the reference """
    return self.ref

  def get_title(self) -> str:
    """ Getter for the page title """
    return self.title

  def get_cves(self) -> List["CVE"]:
    """ Getter to retreive page cves """
    cves = self.content.get_cves()
    
    if cves is not None:
      cves = cves.values()

    return cves

  def connect(self) -> None:
    """ Connects to a CERTFR page based on given ref """
     # Handle possible connection error
    try:
      req = requests.get(self.link)
      
      if req.status_code != 200:
        raise ConnectionError(f"Error while trying to connect to {self.ref}")
      
      self.raw_content = BeautifulSoup(req.content, 'html.parser')
      self.title = self.raw_content.title.text

      print(self.title)

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
      self.meta = CERTFRPageMeta(meta_section=sections[0])
      self.meta.parse()

      # Content parsing
      self.content = CERTFRPageContent(content_section=sections[1])
      self.content.parse()

    except Exception as e:
      ColorPrint.red(
          f"CERTFRPage::A parsing error occured for {self.ref}\n{e}")

  def to_string(self) -> str:
    """ Converts current instance into a string """
    return f"{self.ref}: {self.title}"

  def to_dictionary(self) -> Dict:
    """ Converts current instance into a dictionary """
    page_dict = {}
    
    if self.meta is not None:
      page_dict= {
        "ref": self.ref,
        "title": self.title,
        **self.meta.to_dictionary(),
        **self.content.to_dictionary(),
      }

    return page_dict

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


class CERTFRPageMeta:
  """ Handles meta table from CERTFR page """
  
  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, meta_section: element):
    """ Constructor """
    self.meta_table = meta_section.find_all("table")[0]
    self.data = None

    self.date_initial: str = None
    self.date_last: str = None
    self.sources: List[str] = None

  # ****************************************************************
  # Methods

  def parse(self) -> None:
    """ Parse meta table """
    meta = {}

    for row in self.meta_table.find_all("tr"):
      cells = row.find_all("td")
      c_name = cells[0].text.strip()
      c_value = cells[-1].text.strip()

      meta[self.clean_str(c_name)] = self.clean_str(c_value)
    
    self.data = meta

  def get_date_initial(self) -> str:
    """ Getter / parser for initial page date """

    if self.data is not None and self.date_initial is None:
      self.date_initial = self.data.get("Date de la première version", None)

    return self.date_initial

  def get_date_last(self) -> str:
    """ Getter / parser for page last change date """
    
    if self.data is not None and self.date_last is None:
      self.date_last = self.data.get("Date de la dernière version", None)

    return self.date_last

  def get_sources(self) -> List[str]:
    """ Getter / parser for page sources """
    
    if self.data is not None and self.sources is None:
      clean_sources = self.data.get("Source(s)", "").split("\n")
      clean_sources = [
        re.sub(r'\s+', ' ', line).strip()
        for line in clean_sources if re.sub(r'\s+', '', line).strip()
      ]

      self.sources = clean_sources

    return self.sources

  def to_dictionary(self) -> Dict:
    """ Converts current instance into a dictionary """
    meta_dict = {}

    if self.data is not None:
      meta_dict = {
        "date_initial": self.get_date_initial(),
        "date_last": self.get_date_last(),
        "sources": self.get_sources()
      }

    return meta_dict

  # ****************************************************************
  # Static methods

  @staticmethod
  def clean_str(str: str) -> str:
    return str.replace("\r", "").strip()



class CERTFRPageContent:
  """ Handles content section from CERTFR page """
  
  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, content_section: element):
    """ Constructor """
    self.content = content_section
    self.data = None

    self.solutions = None
    self.description = None
    self.risks: Set[str] = None
    self.cves: Dict["CVE"] = None
    self.documentations: List[str] = None
    self.affected_products: List[str] = None

  # ****************************************************************
  # Methods

  def get_risks(self, short: bool = True) -> Set["RiskType"]:
    """ Getter / parser for the list of risks """
    
    if self.data is not None and self.risks is None:
      risk_set = set()

      for risk in list(RiskType):
        if risk.value["fr"].lower() in [ r.lower() for r in self.data.get("Risques", []) ]:
          risk_set.add(risk)

      self.risks = risk_set

    return self.risks

  def get_products(self) -> List[str]:
    """ Getter / parser for affected products """

    if self.data is not None and self.affected_products is None:
      self.affected_products = self.data.get("Systèmes affectés", [])

    return self.affected_products
  
  def get_description(self) -> str:
    """ Getter / parser for description """
    
    if self.data is not None and self.description is None:
      self.description = self.data.get("Résumé", None)
      
    return self.description

  def get_solutions(self) -> str:
    """ Getter / parser for solutions """
    
    if self.data is not None and self.solutions is None:
      self.solutions = self.data.get("Solutions", None)

    return self.solutions

  def get_cves(self) -> List[str]:
    """ Returns the refs of all the related cves """

    if self.data is not None and self.cves is None:
      cves = {}

      for cve in self.data.get("CVEs", []):
        if cve not in cves.keys():
          cves[cve] = CVE(ref=cve)

      self.cves = cves
        
    return self.cves

  def get_documentations(self, filter: str = None) -> List[str]:
    """ Getter for the documentations """
    
    if self.data is not None and self.documentations is None:
      self.documentations = self.data.get("Documentation", [])

    docs = self.documentations

    if filter is not None and filter != "":
      docs = [ d for d in self.documentations if filter not in d ]

    return docs

  def parse(self) -> None:
    """ Parse content section """
    data = {}

    titles = self.content.find_all("h2")

    for t in titles:
      next_el = t.find_next_sibling()

      if next_el.name == "ul":
        data[t.text] = [ li.text for li in next_el.find_all("li") ]
        
      else:
        data[t.text] = next_el.text
        
    data["CVEs"] = set(re.findall(CVE_REGEX, self.content.text))
    data["Documentation"] = re.findall(URL_REGEX, self.content.text)

    self.data = data

  def to_dictionary(self) -> Dict:
    """ Converts current instance into a dictionary """
    content_dict = {}

    if self.data is not None:
      content_dict = {
        "risks": [ r.name for r in self.get_risks() ],
        "products": self.get_products(),
        "description": self.get_description(),
        "cves": [ cve.get_ref() for cve in self.get_cves().values() ],
        "solutions": self.get_solutions(),
        "documentations": self.get_documentations(filter="cve.org")
      }

    return content_dict