""" Module to parse NIST CVE page in order to retreive CVE data """
import requests
from bs4 import BeautifulSoup


def extract_cvss(content):
  """ Function to extract CVSS score """
  cvss_soup = content.find_all(id="Cvss3NistCalculatorAnchor")
  return float(cvss_soup[0].text.split(" ")[0]) if len(cvss_soup) > 0 else -1


def extract_description(content):
  """ Function to extract description """
  desc_soup = content.select("p[data-testid='vuln-description']")
  return desc_soup[0].text if len(desc_soup) > 0 else ""


def extract_publish_date(content):
  """ Function to extract cve publish date """
  p_date_soup = content.select("span[data-testid='vuln-published-on']")
  return p_date_soup[0].text if len(p_date_soup) > 0 else ""


def parse_nist_cve(self, target, mode="default"):
  """ Function to parse NIST CVE page in order to retreive CVE data """

  url = f"https://nvd.nist.gov/vuln/detail/{target}"
  
  # Handle if the target is unreachable
  try:
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')

  except ConnectionError as e:
    self.handle_exception(e, f"Error while requesting {url}. Make sure the target is accessible")

  # Minimal information retreived is the CVSS score
  target_infos = {
    "cve": target,
    "cvss": extract_cvss(soup),
  }

  # If default mode : more informations are retreived
  if mode == "default":
    target_infos = {
      **target_infos,
      "publish_date": extract_publish_date(soup),
      "description": extract_description(soup),
      "link": url
    }

  print(f"{target}: {target_infos['cvss']}")

  return target_infos
