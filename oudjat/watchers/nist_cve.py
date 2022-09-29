""" Module to parse NIST CVE page in order to retreive CVE data """
import requests
from bs4 import BeautifulSoup


def extract_cvss(content):
  """ Function to extract CVSS score """
  cvss_soup = content.find_all(id="Cvss3NistCalculatorAnchor")
  return float(cvss_soup[0].text.split(" ")[0]) if len(cvss_soup) > 0 else ""


def extract_description(content):
  """ Function to extract description """
  desc_soup = content.select("p[data-testid='vuln-description']")
  return desc_soup[0].text if len(desc_soup) > 0 else ""


def extract_publish_date(content):
  """ Function to extract cve publish date """
  p_date_soup = content.select("span[data-testid='vuln-published-on']")
  return p_date_soup[0].text if len(p_date_soup) > 0 else ""


def parse_nist_cve(self, target):
  """ Function to parse NIST CVE page in order to retreive CVE data """
  url = f"https://nvd.nist.gov/vuln/detail/{target}"

  try:
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')

  except ConnectionError as e:
    self.handle_exception(e, f"Error while requesting {url}. Make sure the target is accessible")

  target_infos = {
    "cve": target,
    "cvss": extract_cvss(soup),
    "publish_date": extract_publish_date(soup),
    "description": extract_description(soup),
    "link": url
  }

  self.results.append(target_infos)

  print(f"\n* {target} *")
  for k, v in target_infos.items():
    print(f"{k}: {v}")
