import requests
from bs4 import BeautifulSoup

def parse_certfr_page(self, target):

  try:
    req = requests.get(target)
    soup = BeautifulSoup(req.content, 'html.parser')

  except Exception as e:
    self.handle_exception(e, f"Error while requesting {target}. Make sure the target is accessible")

  article_sections = soup.article.find_all("section")

  keys = ["ref", "title", "date_initial", "date_last", "sources", "risks", "affected_products", "link"]
  values = []

  extract_meta_infos(article_sections[0], values)
  extract_risks(article_sections[1], values)
  extract_affected_products(article_sections[1], values)

  values.append(target)

  print(split_doc_list(article_sections[1]))

  # Setup the dictionary
  items = dict(zip(keys, values))
  self.results.append(items)
  
  print(f"\n* {target} *")
  for item in items.items():
    print("{} : {}".format(*item))


def extract_meta_infos(meta, values):
  tab_items = extract_table_infos(meta.find_all(class_="table-condensed")[0])
  tab_values = [*tab_items.values()]

  for i in range(len(tab_values) - 1):
    values.append(tab_values[i])


def extract_table_infos(tab):
  tab_rows = [ r.find_all("td") for r in tab.find_all("tr") ]
  return dict([ (k.text, v.text) for k, v in tab_rows ])


def extract_list_infos(list):
  return [ li.text for li in list.find_all("li") ]


def extract_risks(content, values):
  risks_labels = [
    "Élévation de privilèges",
    "Exécution de code arbitraire à distance",
    "Déni de service à distance",
    "Contournement de la politique de sécurité",
    "Atteinte à la confidentialité des données",
    "Atteinte à l'intégrité des données"
  ]
  risks_tg = [ "EOP", "RCE", "DOS", "SFB", "ID", "TMP" ]
  risks_flist = [ risks_tg[risks_labels.index(risk)] for risk in extract_list_infos(content.find_all("ul")[0]) ]

  values.append(";".join(risks_flist))


def extract_affected_products(content, values):
  values.append("\n".join(extract_list_infos(content.find_all("ul")[1])))


def split_doc_list(content):
  doc_list = extract_doc_list(content.find_all("ul")[2])

  cve, docs = [], []
  for el in doc_list:
    if el["text"].__contains__("CVE"):
      cve.append(el["text"][-13:])
    else:
      docs.append(el["link"])

  return { "cve": cve, "docs": docs }



def extract_doc_list(list):
  res = []

  for item in list.find_all("li"):
    splitted = item.text.replace("\n", "").split(" http")
    res.append({ "text": splitted[0], "link": "http" + splitted[1] })

  return res