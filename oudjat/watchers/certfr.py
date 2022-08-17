""" Several functions that aim to parse a certfr page """
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
  keys = [ "ref", "title", "date_initial", "date_last", "sources" ]
  tab_items = extract_table_infos(meta.find_all(class_="table-condensed")[0])
  return { keys[i]: [*tab_items.values()][i] for i in range(len(keys)) }


def extract_products(content):
  """ Generates a list of affected products based on the corresponding <ul> element """
  return { "products": "\n".join(extract_list_infos(content.find_all("ul")[1])) }


def extract_doc_list(ul):
  """ Extracts data from the certfr documentation list """
  res = []

  for item in ul.find_all("li"):
    splitted = item.text.replace("\n", "").split(" http")
    res.append({ "text": splitted[0], "link": "http" + splitted[1] })

  return res


def extract_cve_docs(content):
  """ Splits the certfr documentation list into a list of the related CVEs and a list of the doc links """
  doc_list = extract_doc_list(content.find_all("ul")[2])

  doc_data = { "cve": [], "docs": [] }
  for doc in doc_list:
    if "CVE" in doc["text"]:
      doc_data["cve"].append(doc["text"][-13:])
    else:
      doc_data["docs"].append(doc["link"])

  return { k: "\n".join(v) for k, v in doc_data.items() }


def extract_risks(content):
  """ Generates a list out of a the <ul> element relative to the risks """
  risks = {
    "N/A": "Non spécifié par l'éditeur",
    "EOP": "Élévation de privilèges",
    "RCE": "Exécution de code",
    "DOS": "Déni de service",
    "SFB": "Contournement",
    "ID" : "Atteinte à la confidentialité des données",
    "TMP": "Atteinte à l'intégrité des données"
  }

  risk_list = extract_list_infos(content.find_all("ul")[0])

  return {
    "risks": ";".join([ [ *risks.keys() ][ get_matching_str([ *risks.values() ], risk) ] for risk in risk_list ])
  }


def get_matching_str(str_list, txt):
  """"""
  for s in str_list:
    if s in txt:
      return str_list.index(s)


def parse_certfr_avis(sections):
  """ Parse a certfr avis page """
  return {
    **extract_meta(sections[0]),
    **extract_risks(sections[1]),
    **extract_products(sections[1]),
    **extract_cve_docs(sections[1]),
  }


def switch_page(page_type):
  """ Returns the correct function based on certfr page type """
  switch = {
    "avis": parse_certfr_avis
  }

  return switch.get(page_type, "Invalid type !")


def parse_certfr_page(self, target):
  """ Main function to parse a certfr page """
  try:
    req = requests.get(target)
    soup = BeautifulSoup(req.content, 'html.parser')

  except Exception as e:
    self.handle_exception(e, f"Error while requesting {target}. Make sure the target is accessible")

  article_sections = soup.article.find_all("section")

  items = switch_page(target.split("/")[3])(article_sections)
  self.results.append({ **items, "link": target })

  print(f"\n* {target} *")
  for item in items.items():
    print(f"{item[0]}: {item[1]}")
