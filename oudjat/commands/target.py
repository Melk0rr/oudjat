import os
import re
import csv
from urllib.parse import urlparse

from .base import Base
from oudjat.utils.color_print import ColorPrint
from oudjat.watchers.certfr import parse_certfr_page

'''Main enumeration module'''
class Target(Base):

  results = list()

  def handle_exception(self, e, message=""):
    if self.options["--verbose"]:
      print(e)
    if message:
      ColorPrint.red(message)


  def is_url(self, url):
    try:
      res = urlparse(url)
      return all([res.scheme, res.netloc, res.path])
    except Exception as e:
      self.handle_exception(e, "Invalid url !")

  
  def res_2_csv(self):
    print("\nExporting results to csv...")
    with open(self.options["--csv"], "w", encoding="utf-8", newline="") as f:
      writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
      writer.writeheader()
      writer.writerows(self.results)


  def init(self):
    # If user set file option: define target with file content
    if self.options["FILE"]:
      full_path = os.path.join(os.getcwd(), self.options["FILE"])

      with open(full_path) as file:
        self.options["TARGET"] = list(filter(None, file.read().split('\n')))

    # Else: the target is defined by the target option
    else: self.options["TARGET"] = list(filter(None, self.options["TARGET"].split(",")))

    # Clean up targets
    for i in range(len(self.options["TARGET"])):
      url = self.options["TARGET"][i]
      # Inject protocol if not there
      if not re.match(r'http(s?):', url):
        url = 'http://' + url

      if self.is_url(url):

        try:
          self.options["TARGET"][i] = url
          ColorPrint.green(f"Gathering data for {url}")
        except Exception as e:
          self.handle_exception(e, f"Error connecting to {url}! Make sure you spelled it correctly and it is a resolvable address")
  

  def run(self):
    # Retreive IP of target and run initial configuration
    self.init()

    for i in range(len(self.options["TARGET"])):
      parse_certfr_page(self, self.options["TARGET"][i])

    if (self.options["--csv"]):
      self.res_2_csv()