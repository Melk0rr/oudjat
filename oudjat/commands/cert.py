""" CVE Target class """
import re
from urllib.parse import urlparse

from oudjat.utils.color_print import ColorPrint
from oudjat.utils.init_option_handle import str_file_option_handle
from oudjat.watchers.certfr import parse_certfr_page

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

    # Handle keywords initialization
    str_file_option_handle(self, "--keywords", "--keywordfile")

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


  def run_max_cve_check(self):
    """ Check for the most severe CVE """
    print(f"\nChecking the highests CVE...")

    for res in self.results:
      cve_max, cvss_max = self.max_cve(res["cve"]).values()
      
      if cve_max:
        if cvss_max == -1:
          msg = f"No CVSS score available for {res['ref']}...\n"
        else:
          msg = f"{res['ref']} highest CVE: {cve_max} ({cvss_max})\n"
      else:
        msg = f"No CVE found for {res['ref']}...\n"

      print(msg)
      res["cve_max"], res["cvss_max"] = cve_max, cvss_max


  def run_keyword_check(self):
    """ Look for provided keywords in the results """
    print(f"\n{len(self.options['--keywords'])} keywords provided. Comparing with results...")

    for res in self.results:
      matched = [ k for k in self.options["--keywords"] if k.lower() in res["title"].lower() ]

      msg = f"No match for {res['ref']}..."
      if len(matched) > 0:
        msg = f"{res['ref']} matched for {'-'.join(matched)}"

      print(msg)
      res["match"] = "-".join(matched)


  def run(self):
    """ Main function called from the cli module """
    self.init()

    for i in range(len(self.options["TARGET"])):
      parse_certfr_page(self, self.options["TARGET"][i])

    # If option is provided: check for the most severe CVE
    if self.options["--check-max-cve"]:
      self.run_max_cve_check()

    # If keywords are provided in any way: compare them with results
    if self.options["--keywords"]:
      self.run_keyword_check()

    if self.options["--export-csv"]:
      super().res_2_csv()
