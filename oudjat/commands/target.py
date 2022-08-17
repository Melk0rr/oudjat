""" Target module handling targeting operations and data gathering """
import os
import re
import csv
from urllib.parse import urlparse

from oudjat.utils.color_print import ColorPrint
from oudjat.watchers.certfr import parse_certfr_page

from .base import Base

class Target(Base):
  """ Main enumeration module """
  results = []

  def handle_exception(self, e, message=""):
    """ Function handling exception for the current class """
    if self.options["--verbose"]:
      print(e)
    if message:
      ColorPrint.red(message)


  def is_url(self, url):
    """ Check whether the provided target is a valid URL """
    try:
      res = urlparse(url)
      return all([res.scheme, res.netloc, res.path])
    except Exception as e:
      self.handle_exception(e, "Invalid url !")
      return False


  def res_2_csv(self):
    """ Write the results into a CSV file """
    print("\nExporting results to csv...")
    with open(self.options["--export-csv"], "w", encoding="utf-8", newline="") as f:
      writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
      writer.writeheader()
      writer.writerows(self.results)

  def init_url(self, index):
    """ Clean url target """
    url = self.options["TARGET"][index]

    # Inject protocol if not there
    if not re.match(r'http(s?):', url):
      url = 'http://' + url

    if self.is_url(url):
      try:
        self.options["TARGET"][index] = url
        ColorPrint.green(f"Gathering data for {url}")

      except Exception as e:
        self.handle_exception(e, f"Error connecting to {url}! Make sure you spelled it correctly and it is a resolvable address")


  def init(self):
    """ Initialization function """
    # If user set file option: define target with file content
    if self.options["FILE"]:
      full_path = os.path.join(os.getcwd(), self.options["FILE"])

      with open(full_path, encoding="utf-8") as f:
        self.options["TARGET"] = list(filter(None, f.read().split('\n')))

    # Else: the target is defined by the target option
    else: self.options["TARGET"] = list(filter(None, self.options["TARGET"].split(",")))

    # Clean up targets
    for i in range(len(self.options["TARGET"])):
      if self.options["--mode"] == "cve":
        print("User set cve mode")
      else:
        self.init_url(i)


  def run(self):
    """ Main function which is called from the cli module """
    # Retreive IP of target and run initial configuration
    self.init()

    for i in range(len(self.options["TARGET"])):
      parse_certfr_page(self, self.options["TARGET"][i])

    if self.options["--export-csv"]:
      self.res_2_csv()
