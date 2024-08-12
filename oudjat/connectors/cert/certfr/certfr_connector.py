""" Several functions that aim to parse a certfr page """
import re
import requests

from enum import Enum
from typing import List, Dict, Union
from datetime import datetime
from bs4 import BeautifulSoup, element

from oudjat.utils.color_print import ColorPrint
from oudjat.model.cve import CVE, CVE_REGEX
from oudjat.connectors.connector import Connector
from oudjat.connectors.cert.risk_types import RiskTypes
from oudjat.connectors.cert.certfr.certfr_page_types import CERTFRPageTypes
from oudjat.connectors.cert.certfr.certfr_page import CERTFRPage

URL_REGEX = r'http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

class CERTFRConnector(Connector):
  """ CERTFR class addressing certfr page behavior """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, ref: str, title: str = None):
    """ Constructor """
    
    super().__init__(
      target=CERTFRPage.BASE_LINK,
      service_name="OudjatCERTFRConnection"
    )

  def connect(self) -> None:
    """ Checks connection to CERTFR """
    try:
      req = requests.get(self.target)
      
      if req.status_code == 200:
        self.connection = True
        
    except ConnectionError as e:
      raise(f"Could not connect to {CERTFRPage.BASE_LINK}\n{e}")

  def search(self, search_filter: Union[str, List[str]]) -> List["CERTFRPage"]:
    """ Search for page or ref in CERTFR website """

    if not self.connection:
      self.connect()
    
    if not isinstance(search_filter, list):
      search_filter = [ search_filter ]
      
    for ref in search_filter:
      page = CERTFRPage(ref)
      page.connect()
      

  # ****************************************************************
  # Parsers

  def parse_cve(self, content: BeautifulSoup) -> None:
    """ Extract all CVE refs in content and look for the highest CVSS """
    cve_refs = set(re.findall(CVE_REGEX, content.text))
    for ref in cve_refs:
      self.cve_list.add(CVE(ref))

    print(f"{len(self.cve_list)} CVEs related to {self.ref}")

  def parse_products(self, content: BeautifulSoup) -> None:
    """ Generates a list of affected products based on the corresponding <ul> element """
    product_list = content.find_all("ul")[1]
    self.affected_products = [li.text for li in product_list.find_all("li")]

  def parse_documentations(self, content: BeautifulSoup) -> None:
    """ Extracts data from the certfr documentation list """
    self.documentations = re.findall(URL_REGEX, content.text)

  def parse_risks(self, content: BeautifulSoup) -> None:
    """ Generates a list out of a the <ul> element relative to the risks """

    for risk in list(RiskTypes):
      if risk.value.lower() in content.text.lower():
        self.risks.add(risk)

  def parse_meta(self, meta_section: element.Tag) -> None:
    """ Parse meta section """
    meta_tab = meta_section.find_all("table")[0]
    tab_cells = {}

    for row in meta_tab.find_all("tr"):
      cells = row.find_all("td")
      c_name = cells[0].text.strip()
      c_value = cells[-1].text.strip()

      tab_cells[self.clean_str(c_name)] = self.clean_str(c_value)

    if not self.title:
      self.title = tab_cells["Titre"]

    self.date_initial = tab_cells["Date de la première version"]
    self.date_last = tab_cells["Date de la dernière version"]
    clean_sources = tab_cells["Source(s)"].split("\n")
    clean_sources = [
      re.sub(r'\s+', ' ', line).strip()
      for line in clean_sources if re.sub(r'\s+', '', line).strip()
    ]
    self.sources = clean_sources

  def parse_content(self, section: element.Tag) -> None:
    """ Parse content section """
    self.parse_cve(section)
    self.parse_risks(section)
    self.parse_products(section)
    self.parse_documentations(section)

  def parse(self) -> None:
    """ Main function to parse a certfr page """
    print(f"\n* Parsing {self.ref} *")

    # Handle possible connection error
    try:
      req = requests.get(self.target)
      soup = BeautifulSoup(req.content, 'html.parser')

    except ConnectionError:
      ColorPrint.red(
          f"Error while requesting {self.ref}. Make sure it is a valid certfr reference")

    # Handle parsing error
    try:
      article_sections = soup.article.find_all("section")
      self.parse_meta(article_sections[0])
      self.parse_content(article_sections[1])

    except Exception as e:
      ColorPrint.red(
          f"A parsing error occured for {self.ref}: {e}\nCheck if the page has the expected format.")

  # ****************************************************************
  # Static methods

  @staticmethod
  def parse_feed(feed_url: str, date_str_filter: str = None) -> List[str]:
    """ Parse a CERTFR Feed page """
    try:
      feed_req = requests.get(feed_url)
      feed_soup = BeautifulSoup(feed_req.content, "xml")

    except Exception as e:
      print(
          e, f"A parsing error occured for {feed_url}: {e}\nCheck if the page has the expected format.")

    feed_items = feed_soup.find_all("item")
    filtered_feed = []

    for item in feed_items:
      certfr_ref = CERTFRConnector.get_ref_from_link(item.link.text)

      if date_str_filter:
        try:
          valid_date_format = "%Y-%m-%d"
          date_filter = datetime.strptime(date_str_filter, valid_date_format)          

          date_str = item.pubDate.text.split(" +0000")[0]
          date = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S")

          if date > date_filter:
            filtered_feed.append(certfr_ref)

        except ValueError as e:
          ColorPrint.red(
              f"Invalid date filter format. Please provide a date filter following the pattern YYYY-MM-DD !")
          
      else:
        filtered_feed.append(certfr_ref)

    return filtered_feed