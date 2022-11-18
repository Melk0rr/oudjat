""" Several functions that aim to parse a certfr page """
import re

import requests
from bs4 import BeautifulSoup


def handle_multiline(value):
  """ Split multiline if necessary """
  return value.split("\n") if "\n" in value else value


def extract_meta(meta):
  """ Extracts meta information from a <table> element """
  meta_tab = meta.find_all("table")[0]
  tab_rows = [ r.find_all("td") for r in meta_tab.find_all("tr") ]
  return [ handle_multiline(r[1].text) for r in tab_rows ]


def extract_products(content):
  """ Generates a list of affected products based on the corresponding <ul> element """
  product_list = content.find_all("ul")[1]
  return [ li.text for li in product_list.find_all("li") ]


def extract_doc_list(ul):
  """ Extracts data from the certfr documentation list """
  res = []

  for item in ul.find_all("li"):
    splitted = item.text.replace("\n", "").split("http")
    res.append({ "text": splitted[0], "link": "http" + splitted[1] })

  return res


def extract_cve(content):
  """ Extract all CVE refs in content and look for the highest CVSS """
  return [ *set(re.findall(r'CVE-\d{4}-\d{4,7}', content.text)) ]


def extract_docs(content):
  """ Splits the certfr documentation list into a list of the related CVEs and a list of the doc links """
  doc_list = extract_doc_list(content.find_all("ul")[-1])
  return [ doc["link"] for doc in doc_list if "Référence CVE" not in doc["text"] ]


def extract_risks(content):
  """ Generates a list out of a the <ul> element relative to the risks """
  risks = {
    "N/A": "Non spécifié par l'éditeur",
    "EOP": "Élévation de privilèges",
    "RCE": "Exécution de code",
    "DOS": "Déni de service",
    "SFB": "Contournement",
    "IDT": "Usurpation",
    "ID" : "Atteinte à la confidentialité",
    "TMP": "Atteinte à l'intégrité",
    "XSS": "Injection de code"
  }

  risk_list = content.find_all("ul")[0].text
  return [ r for r, d in risks.items() if d.lower() in risk_list.lower() ]


def generic_extract(section):
  extracts = {
    "cve": extract_cve,
    "risks": extract_risks,
    "products": extract_products,
    "docs": extract_docs
  }

  return { k: f(section) for k, f in extracts.items() }


def parse_certfr_avis(sections):
  """ Parse a certfr avis page """
  meta_keys = [ "ref", "title", "date_initial", "date_last", "sources" ]
  meta_props = dict(zip(meta_keys, extract_meta(sections[0])))

  print(f"{meta_props['title']}\nPublished on {meta_props['date_initial']}")
  return { **meta_props, **generic_extract(sections[1]) }


def switch_page(page_type):
  """ Returns the correct function based on certfr page type """
  switch = {
    "avis": parse_certfr_avis,
    "alerte": parse_certfr_avis
  }

  return switch.get(page_type, "Invalid type !")


def parse_certfr_page(self, target):
  """ Main function to parse a certfr page """

  print(f"\n* {target} *")

  # Handle possible connection error
  try:
    req = requests.get(target)
    soup = BeautifulSoup(req.content, 'html.parser')

  except ConnectionError as e:
    self.handle_exception(e, f"Error while requesting {target}. Make sure the target is accessible")

  # Handle parsing error
  try:
    article_sections = soup.article.find_all("section")
    target_infos = switch_page(target.split("/")[3])(article_sections)

    res = { **target_infos, "link": target }
    self.results.append(res)

  except Exception as e:
    self.handle_exception(e, f"A parsing error occured for {target}: {e}\nCheck if the page has the expected format.")
