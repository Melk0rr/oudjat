""" Target module handling targeting operations and data gathering """
import csv
import json
from time import sleep
from multiprocessing import Pool

from oudjat.utils.color_print import ColorPrint
from oudjat.utils.file import import_csv, export_csv

from .base import Base
from oudjat.control.data import DataFilter, DataScope
from oudjat.control.kpi import KPIGroup

class KPIFactory(Base):
  """Main enumeration module"""
  
  def __init__(self, options):
    """ Constructor """
    super().__init__(options)

    config_file = open(self.options["--config"])
    self.config = json.load(config_file)

    print("Importing sources...")
    self.data_sources = {}
    config_ds = self.config["data_sources"]

    for k in config_ds.keys():
      source_path = f"{self.options['DIRECTORY']}\{config_ds[k]}.csv"
      self.data_sources[k] = import_csv(source_path, delimiter='|')

    self.filters = { k: DataFilter(fieldname=f["field"], value=f["value"]) for k, f in self.config["filters"].items() }
    self.scopes = {}
    for k, s in self.config["scopes"].items():
      s_filters = [ self.filters[f] for f in s["filters"] ]
      self.scopes[k] = DataScope(name=s["name"], perimeter=s["perimeter"], data=self.data_sources[kpi["perimeter"]], filters=s_filters)

    self.kpis = [ KPIGroup(kpi, data_source=self.data_sources[kpi["perimeter"]]) for kpi in self.config["kpi_groups"] ]
    self.results = []

  def handle_exception(self, e, message=""):
    """ Function handling exception for the current class """
    if self.options["--verbose"]:
      print(e)
      
    if message:
      ColorPrint.red(message)

  def kpi_process(self, kpi):
    """ Target process to deal with url data """
    kpi_res = kpi.get_values()
    kpi.print_values()

    return kpi_res

  def kpi_thread_loop(self):
    """ Run kpi thread loop """
    with Pool(processes=5) as pool:
      for kpi_res in pool.imap_unordered(self.kpi_process, self.kpis):
        self.results.extend(kpi_res)

  def run(self):
    """ Run command method """
    if self.options["--history"]:
      print("")
    else:
      self.kpi_thread_loop()

    if self.options["--export-csv"]:
      export_csv(self.results, self.options["--export-csv"], delimiter='|')