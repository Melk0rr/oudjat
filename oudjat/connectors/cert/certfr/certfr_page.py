import re
import requests

from typing import List, Dict, Set, Union
from bs4 import BeautifulSoup, element

from oudjat.utils.color_print import ColorPrint
from oudjat.model.cve import CVE
from oudjat.connectors.cert.certfr.certfr_page_types import CERTFRPageTypes
from oudjat.connectors.cert.certfr.certfr_page_meta import CERTFRPageMeta
from oudjat.connectors.cert.certfr.certfr_page_content import CERTFRPageContent

REF_TYPES = '|'.join([ pt.name for pt in CERTFRPageTypes ])
LINK_TYPES = '|'.join([ pt.value for pt in CERTFRPageTypes ])
CERTFR_REF_REGEX = rf"CERTFR-\d{{4}}-(?:{REF_TYPES})-\d{{3,4}}"
CERTFR_LINK_REGEX = rf"https:\/\/www\.cert\.ssi\.gouv\.fr\/(?:{LINK_TYPES})\/{CERTFR_REF_REGEX}"

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

    self.CVE_RESOLVED = False

    # Set page type
    ref_type = re.search(rf"(?:{REF_TYPES})", self.ref).group(0)
    self.page_type = CERTFRPageTypes[ref_type].value
    
    self.link = f"{self.BASE_LINK}/{self.page_type}/{self.ref}/"

  # ****************************************************************
  # Methods

  def get_ref(self) -> str:
    """ Getter for the reference """
    return self.ref

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