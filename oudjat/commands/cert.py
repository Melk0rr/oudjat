""" CVE Target class """
import re
import socket
from urllib.parse import urlsplit

from oudjat.utils.color_print import ColorPrint
from oudjat.utils.init_option_handle import str_file_option_handle
from oudjat.watchers.certfr import parse_certfr_page

from .target import Target


class CERT(Target):
  """ CVE Target """

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

      parsed = urlsplit(url)
      host = parsed.netloc

      try:
        socket.gethostbyname(host)

      except ConnectionError as e:
        self.handle_exception(e,
                              f"Error connecting to {url}! Make sure it is a resolvable address")

      self.options["TARGET"][i] = url
      ColorPrint.green(f"Gathering data for {url}")

  def max_cve_check(self, target):
    """ Check for the most severe CVE """
    print(f"\nChecking {target['ref']} highest CVE...")

    cve_max, cvss_max = self.max_cve(target["cve"]).values()

    if cve_max:
      if cvss_max == -1:
        msg = f"No CVSS score available for {target['ref']}...\n"
      else:
        msg = f"{target['ref']} highest CVE: {cve_max} ({cvss_max})\n"
    else:
      msg = f"No CVE found for {target['ref']}...\n"

    print(msg)
    return [cve_max, cvss_max]

  def keyword_check(self, target):
    """ Look for provided keywords in the results """

    matched = [k for k in self.options["--keywords"]
               if k.lower() in target["title"].lower()]

    msg = f"No match for {target['ref']}..."
    if len(matched) > 0:
      msg = f"{target['ref']} matched for {'-'.join(matched)}"

    print(msg)
    return matched

  def run(self):
    """ Main function called from the cli module """
    self.init()

    for i in range(len(self.options["TARGET"])):
      target_data = parse_certfr_page(self, self.options["TARGET"][i])

      # If option is provided: check for the most severe CVE
      if self.options["--check-max-cve"]:
        target_data["cve_max"], target_data["cvss_max"] = self.max_cve_check(
            target_data)

      # If keywords are provided in any way: compare them with results
      if self.options["--keywords"]:
        target_data["match"] = "-".join(self.keyword_check(target_data))

    if self.options["--export-csv"]:
      super().res_2_csv()
