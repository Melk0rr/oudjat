""" Several functions that aim to parse a certfr page """
import re
import requests
from bs4 import BeautifulSoup


def extract_table_infos(tab):
  """ Generates a dictionary out of a <table> element """
  tab_rows = [ r.find_all("td") for r in tab.find_all("tr") ]
  return { k.text: v.text for k, v in tab_rows }


def extract_list_infos(ul_list):
  """ Generates a collection out of a <ul> element """
  return [ li.text for li in ul_list.find_all("li") ]


def extract_meta(meta):
  """ Extracts meta information from a <table> element"""
  tab_items = extract_table_infos(meta.find_all(class_="table-condensed")[0])
  return [ *tab_items.values() ]


def extract_products(content):
  """ Generates a list of affected products based on the corresponding <ul> element """
  return extract_list_infos(content.find_all("ul")[1])


def extract_doc_list(ul):
  """ Extracts data from the certfr documentation list """
  res = []

  for item in ul.find_all("li"):
    splitted = item.text.replace("\n", "").split("http")
    print(splitted)
    res.append({ "text": splitted[0], "link": "http" + splitted[1] })

  return res


def extract_cve(content):
  """ Extract all CVE refs in content """
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
    "ID" : "Atteinte à la confidentialité des données",
    "TMP": "Atteinte à l'intégrité des données"
  }

  risk_list = extract_list_infos(content.find_all("ul")[0])

  return [ get_matching_str([ *risks.items() ], risk) for risk in risk_list ]


def get_matching_str(risks, txt):
  """ Returns the trigram corresponding to the matching risk """
  return next((r[0] for r in risks if r[1] in txt), txt)


def parse_certfr_avis(self, sections):
  """ Parse a certfr avis page """
  meta_keys = [ "ref", "title", "date_initial", "date_last", "sources" ]
  cve = extract_cve(sections[1])
  cve_high = self.max_cve(cve) if len(cve) > 0 else { "cve": "", "cvss": None }

  return {
    **dict(zip(meta_keys, extract_meta(sections[0]))),
    "cve": "\n".join(cve),
    "cve_high": cve_high["cve"],
    "cvss_high": cve_high["cvss"],
    "risks": "\n".join(extract_risks(sections[1])),
    "products": "\n".join(extract_products(sections[1])),
    "docs": "\n".join(extract_docs(sections[1]))
  }


def switch_page(page_type):
  """ Returns the correct function based on certfr page type """
  switch = {
    "avis": parse_certfr_avis,
    "alerte": parse_certfr_avis
  }

  return switch.get(page_type, "Invalid type !")


def parse_certfr_page(self, target):
  """ Main function to parse a certfr page """

  # Handle possible connection error
  try:
    req = requests.get(target)
    soup = BeautifulSoup(req.content, 'html.parser')

  except ConnectionError as e:
    self.handle_exception(e, f"Error while requesting {target}. Make sure the target is accessible")

  # Default values
  target_infos = {
    "ref": target.split("/")[-2],
    "title": None,
    "date_initial": None,
    "date_last": None,
    "sources": None,
    "cve": None,
    "risks": None,
    "products": None,
    "docs": None,
    "link": target
  }

  # Handle parsing error
  try:
    article_sections = soup.article.find_all("section")
    target_infos = switch_page(target.split("/")[3])(self, article_sections)

  except Exception as e:
    self.handle_exception(e, f"A parsing error occured for {target}.")

  print(f"\n* {target} *")
  for k, v in target_infos.items():
    print(f"{k}: {v}")

  return { **target_infos, "link": target }
