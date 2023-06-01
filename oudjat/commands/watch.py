""" CVE Target class """
import re
import socket
from urllib.parse import urlsplit

from oudjat.utils.color_print import ColorPrint
from oudjat.utils.init_option_handle import str_file_option_handle
from oudjat.watchers.certfr import CERTFR

from .target import Target


class Watch(Target):
  """ CVE Target """

  def __init__(self, options):
    """ Constructor """
    super().__init__(options)

    # Handle keywords initialization
    if self.options["--keywords"] or self.options["--keywordfile"]:
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
      ColorPrint.green(f"Gathering data from {url}")

  def keyword_check(self, target):
    """ Look for provided keywords in the results """

    matched = [k for k in self.options["--keywords"]
               if k.lower() in target.get_title().lower()]

    msg = f"No match for {target.get_ref()}..."
    if len(matched) > 0:
      msg = f"{target.get_ref()} matched for {'-'.join(matched)}"

    print(msg)
    return matched

  def run_parsing(self, target):
    """ Define parsing instructions to run over all final targets """
    target.parse()
    target_data = target.to_dictionary()

    # If option is provided: check for the most severe CVE
    if self.options["--check-max-cve"]:
      max_cve = target.get_max_cve(cve_data=self.options["--cve-list"])
      max_cve_dict = max_cve.to_dictionary()
      target_data["cve_max"], target_data["cvss_max"] = max_cve_dict.values()

    # If keywords are provided in any way: compare them with results
    if self.options["--keywords"]:
      target_data["match"] = "-".join(self.keyword_check(target))

    return target_data

  def run(self):
    """ Main function called from the cli module """

    for i in range(len(self.options["TARGET"])):
      # If option is provided: retreive alerts from rss feed
      if self.options["--feed"]:
        alert_items = CERTFR.parse_feed(
            self.options["TARGET"][i], self.options["--filter"])

        for item in alert_items:
          self.results.append(self.run_parsing(item))

        print(
            f"\n{len(self.results)} alerts since the {self.options['--filter']}")

      else:
        self.results.append(
            self.run_parsing(CERTFR(self.options["TARGET"][i])))

    if self.options["--export-csv"]:
      super().res_2_csv()
