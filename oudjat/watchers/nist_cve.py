""" Module to parse NIST CVE page in order to retreive CVE data """
import json

import requests


def parse_nist_cve(target, mode="default"):
  """ Function to parse NIST CVE page in order to retreive CVE data """

  url = f"https://nvd.nist.gov/vuln/detail/{target}"
  api_url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={target}/"

  print(api_url)

  # Handle if the target is unreachable
  try:
    response = requests.get(api_url)
    print(response)

  except ConnectionError as e:
    print(
        e, f"Error while retreiving {target} data. Make sure it is a valid CVE")

  # # Minimal information retreived is the CVSS score
  # target_infos = {
  #     "cve": target,
  #     "cvss": req.v31score,
  #     "severity": req.v31severity
  # }

  # # If default mode : more informations are retreived
  # if mode == "default":
  #   target_infos = {
  #       **target_infos,
  #       "publish_date": req.published,
  #       "description": req.descriptions[0].value,
  #       "link": url
  #   }

  # print(f"{target}: {target_infos['cvss']}")
  # return target_infos

parse_nist_cve("CVE-2022-2880")