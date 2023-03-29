""" Module to parse NIST CVE page in order to retreive CVE data """
import nvdlib


def parse_nist_cve(target, mode="default", api_key=None):
  """ Function to parse NIST CVE page in order to retreive CVE data """

  url = f"https://nvd.nist.gov/vuln/detail/{target}"

  # Handle if the target is unreachable
  try:
    req = nvdlib.searchCVE(cveId=target, key=api_key)[0]

  except ConnectionError as e:
    print(
        e, f"Error while retreiving {target} data. Make sure it is a valid CVE")

  # Minimal information retreived is the CVSS score
  target_infos = {
      "cve": target,
      "cvss": req.v31score,
      "severity": req.v31severity
  }

  # If default mode : more informations are retreived
  if mode == "default":
    target_infos = {
        **target_infos,
        "publish_date": req.published,
        "description": req.descriptions[0].value,
        "link": url
    }

  print(f"{target}: {target_infos['cvss']}")
  return target_infos

parse_nist_cve("CVE-2022-2880")