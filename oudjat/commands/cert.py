""" CVE Target class """
import re
from urllib.parse import urlparse

from oudjat.utils.color_print import ColorPrint
from oudjat.watchers.certfr import parse_certfr_page
from oudjat.watchers.nist_cve import parse_nist_cve

from .target import Target

class CERT(Target):
  """ CVE Target """

  def is_url(self, url):
    """ Check whether the provided target is a valid URL """
    try:
      res = urlparse(url)
      return all([res.scheme, res.netloc, res.path])
    except ValueError as e:
      self.handle_exception(e, f"Invalid url {url}!")
      return False


  def init(self):
    """ Clean url target """
    super().init()

    for i in range(len(self.options["TARGET"])):
      url = self.options["TARGET"][i]

      # Inject protocol if not there
      if not re.match(r'http(s?):', url):
        url = 'http://' + url

      if self.is_url(url):
        try:
          self.options["TARGET"][i] = url
          ColorPrint.green(f"Gathering data for {url}")

        except ConnectionError as e:
          self.handle_exception(e,
          f"Error connecting to {url}! Make sure you spelled it correctly and it is a resolvable address")


  def run(self):
    """ Main function called from the cli module """
    self.init()

    for i in range(len(self.options["TARGET"])):
      vuln = parse_certfr_page(self, self.options["TARGET"][i])
      cves = [ parse_nist_cve(self, cve) for cve in vuln["cve"].split("\n") ]
      cve_high = max(cves, key=lambda x:x["cvss"])

      print(f"highest cve: {cve_high['cve']} / {cve_high['cvss']}")
      self.results.append({ **vuln, "cve_high": cve_high["cve"], "cvss_high": cve_high["cvss"] })

    if self.options["--export-csv"]:
      super().res_2_csv()
