""" CVE Target class """
from typing import List, Dict
from multiprocessing import Pool

from oudjat.utils import ColorPrint
from oudjat.utils import str_file_option_handle
from oudjat.model.vulnerability import CVE
from oudjat.connectors.cert import CERTFRPage
from oudjat.connectors.cert import CERTFRConnector

from . import Target


class Cert(Target):
  """ CVE Target """

  def __init__(self, options: Dict):
    """ Constructor """
    super().__init__(options)

    self.connector = CERTFRConnector()
    self.connector.connect()

    self.unique_targets = set()

    # Handle keywords initialization
    if self.options["--keywords"] or self.options["--keywordfile"]:
      str_file_option_handle(self, "--keywords", "--keywordfile")

    # If option is provided: retreive alerts from rss feed
    if self.options["--feed"]:
      print("Parsing CERT pages from feed...")
      
      feed_items = CERTFRConnector.parse_feed(self.options["TARGET"][0], self.options["--filter"])
      self.options["TARGET"] = feed_items

      print(f"\n{len(feed_items)} alerts since the {self.options['--filter']}")

    for target in self.options["TARGET"]:
      if CERTFRPage.is_valid_ref(target) or CERTFRPage.is_valid_link(target):
        self.unique_targets.add(target)
        ColorPrint.green(f"Gathering data from {target}")

      else:
        ColorPrint.red(f"Error connecting to {target}! Make sure it is a resolvable address")      

  def keyword_check(self, target: "CERTFRPage") -> List[str]:
    """ Look for provided keywords in the results """
    matched = [k for k in self.options["--keywords"]
               if k.lower() in target.get_title().lower()]

    msg = f"No match for {target.get_ref()}..." 
    if len(matched) > 0:
      msg = f"\n{target.get_ref()} matched for {'-'.join(matched)}"

    print(msg)
    return matched

  def cert_process(self, target) -> Dict:
    """ CERT process method to deal with cert data """
    cert_data = {}
    
    try:
      cert_page = self.connector.search(search_filter=target)[0]
      cert_data = cert_page.to_dictionary()

      CVE.resolve_cve_data(cves=cert_page.get_cves(), cve_data=self.options["--cve-list"])
      max_cves = CVE.max_cve(cert_page.get_cves())

      if len(max_cves) > 0:
        cert_data["cves"] = [ cve.get_ref() for cve in max_cves ]
        cert_data["cvss"] = max_cves[0].get_cvss()
        cert_data["documentations"].extend([ cve.get_link() for cve in max_cves ])

        # Joins lists if any
        if self.options["--export-csv"]:
          for k, v in cert_data.items():
            if isinstance(v, list):
              cert_data[k] = ','.join(v)
      
      else:
        cert_data["cvss"] = 0

      # If keywords are provided in any way: compare them with results
      if self.options["--keywords"]:
        cert_data["match"] = '-'.join(self.keyword_check(cert_page))
    
    except Exception as e:
      ColorPrint.red(f"An error occured while processing {target}\n{e}")

    return cert_data

  def run(self) -> None:
    """ Main method called from the cli module """
    
    with Pool(processes=5) as pool:
      for cert_data in pool.imap_unordered(self.cert_process, self.unique_targets):
        self.results.append(cert_data)
      

    if self.options["--export-csv"]:
      super().res_2_csv()
