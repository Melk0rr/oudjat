""" Several functions that aim to parse a certfr page """
import re
import requests

from enum import Enum
from typing import List, Dict, Union
from datetime import datetime
from bs4 import BeautifulSoup, element

from oudjat.utils.color_print import ColorPrint
from oudjat.connectors.connector import Connector
from oudjat.connectors.cert.certfr.certfr_page import CERTFRPage


class CERTFRConnector(Connector):
  """ CERTFR class addressing certfr page behavior """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(self):
    """ Constructor """
    
    super().__init__(
      target=CERTFRPage.BASE_LINK,
      service_name="OudjatCERTFRConnection"
    )

  # ****************************************************************
  # Methods

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

    res = []

    if not self.connection:
      self.connect()
    
    if not isinstance(search_filter, list):
      search_filter = [ search_filter ]

    search_filter = set(search_filter)
      
    for ref in search_filter:
      ColorPrint.blue(ref)
      
      page = CERTFRPage(ref)
      page.connect()
      page.parse()
      
      res.append(page)
    
    return res      

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