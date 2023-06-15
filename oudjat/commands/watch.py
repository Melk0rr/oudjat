""" CVE Target class """
from oudjat.utils.color_print import ColorPrint
from oudjat.utils.init_option_handle import str_file_option_handle
from oudjat.watchers.certfr import CERTFR, parse_feed

from .target import Target


class Watch(Target):
  """ CVE Target """

  def __init__(self, options):
    """ Constructor """
    super().__init__(options)

    self.unique_targets = set()

    # Handle keywords initialization
    if self.options["--keywords"] or self.options["--keywordfile"]:
      str_file_option_handle(self, "--keywords", "--keywordfile")

    # If option is provided: retreive alerts from rss feed
    if self.options["--feed"]:
      print("Parsing CERT pages from feed...")
      
      feed_items = parse_feed(self.options["TARGET"][0], self.options["--filter"])
      self.options["TARGET"] = feed_items

      print(f"\n{len(feed_items)} alerts since the {self.options['--filter']}")

    for target in self.options["TARGET"]:
      if CERTFR.is_valid_ref(target) or CERTFR.is_valid_link(target):
        self.unique_targets.add(target)
        ColorPrint.green(f"Gathering data from {target}")

      else:
        ColorPrint.red(f"Error connecting to {target}! Make sure it is a resolvable address")      

  def keyword_check(self, target):
    """ Look for provided keywords in the results """
    matched = [k for k in self.options["--keywords"]
               if k.lower() in target.get_title().lower()]

    msg = f"No match for {target.get_ref()}..." 
    if len(matched) > 0:
      msg = f"\n{target.get_ref()} matched for {'-'.join(matched)}"

    print(msg)
    return matched

  def run(self):
    """ Main function called from the cli module """
    for target in list(self.unique_targets):
      cert_page = CERTFR(ref=target)

      """ Define parsing instructions to run over all final targets """
      cert_page.parse()
      cert_data = cert_page.to_dictionary()

      # If option is provided: check for the most severe CVE
      if self.options["--check-max-cve"]:
        max_cve = cert_page.get_max_cve(cve_data=self.options["--cve-list"])
        max_cve_dict = max_cve.to_dictionary() if max_cve else { "ref": "", "cvss": None }
        cert_data["cve_max"], cert_data["cvss_max"] = max_cve_dict.values()

      # If keywords are provided in any way: compare them with results
      if self.options["--keywords"]:
        cert_data["match"] = "-".join(self.keyword_check(cert_page))

      self.results.append(cert_data)

    if self.options["--export-csv"]:
      super().res_2_csv()
