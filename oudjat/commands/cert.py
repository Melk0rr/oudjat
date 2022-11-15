""" CVE Target class """
import os
import re
from urllib.parse import urlparse

from oudjat.utils.color_print import ColorPrint
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
    if self.options["--keywordfile"]:
      full_path = os.path.join(os.getcwd(), self.options["--keywordfile"])

      with open(full_path, encoding="utf-8") as f:
        self.options["--keywords"] = list(filter(None, f.read().split('\n')))

    elif self.options["--keywords"]:
      self.options["--keywords"] = list(filter(None, self.options["--keywords"].split(",")))

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
      parse_certfr_page(self, self.options["TARGET"][i])

    # If keywords are provided in any way: compare them with results
    if self.options["--keywords"]:
      print(f"\n{len(self.options['--keywords'])} keywords provided. Comparing with results...")

      for res in self.results:
        matched = [ x for x in self.options["--keywords"] if x.lower() in res["title"].lower() ]
        res["match"] = "-".join(matched)

    if self.options["--export-csv"]:
      super().res_2_csv()
