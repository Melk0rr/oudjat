""" Target module handling targeting operations and data gathering """
import os
import csv
import json
import glob
from datetime import datetime
from multiprocessing import Pool
from typing import List, Dict

from oudjat.utils.color_print import ColorPrint
from oudjat.utils.file import import_csv, export_csv

from .base import Base
from oudjat.control.data import DataFilter, DataScope
from oudjat.control.kpi import KPI, KPIHistory

class KPIFactory(Base):
  """Main enumeration module"""
   
  def __init__(self, options):
    """ Constructor """
    super().__init__(options)

    config_file = open(self.options["--config"])
    self.config = json.load(config_file)

    self.data_sources = {}
    self.filters = {}
    self.scopes = {}

    if not self.options["--history"]:
      sources = { k: { "path": p } for k, p in self.config["data_sources"].items() }
      self.set_data_sources(sources)
      self.set_filters(self.config["filters"])
      self.set_scopes(self.config["scopes"])

    self.kpi_list = self.config["kpis"]
    self.dates = []
    self.kpi_hist = {}
    self.results = []
  
  def set_data_sources(self, sources: Dict, rawPath: bool = False):
    """ Setter for data sources """
    print(f"Importing {', '.join(sources.keys())} sources...")
    formated_sources = {}

    for k in sources.keys():
      source_path = sources[k]["path"]
      if not rawPath:
        source_path = glob.glob(f"{self.options['DIRECTORY']}\{source_path}*.csv")[0]

      base_data = import_csv(source_path, delimiter='|')
      formated_sources[k] = { "data": base_data, "date": self.get_file_date(source_path) }

    self.data_sources = formated_sources

  def set_filters(self, filters: Dict):
    """ Setter for filters """
    self.filters = { k: DataFilter(fieldname=f["field"], value=f["value"]) for k, f in filters.items() }

  def set_scopes(self, scopes: Dict):
    """ Setter for scopes """
    for k, s in scopes.items():
      s_filters = [ self.filters[f] for f in s["filters"] ]
      data_source = self.data_sources[s["perimeter"]]["data"]
      self.scopes[k] = DataScope(name=s["name"], perimeter=s["perimeter"], data=data_source, filters=s_filters)

  def get_file_date(self, path: str):
    """ Retreive file creation date """
    return datetime.fromtimestamp(os.path.getctime(path))

  def build_file_history(self, match: str):
    """ List files based on history, gap and provided directory """

    # List files in provided directory, retreive their creation date and sort them from newer to older
    files = glob.glob(f"{self.options['DIRECTORY']}/{match}*.csv")
    files = [ { "path": f, "date": self.get_file_date(f) } for f in files ]
    files = sorted(files, key=lambda d: d["date"], reverse=True)

    if len(files) == 0:
      ColorPrint.red(f"No files matching {match} in {self.options['DIRECTORY']}")
      return []

    # Narrow file list based on history and gap parameters
    self.dates.append(files[0]["date"])
    history_files = [ files[0] ]
    for f in files:
      if len(history_files) >= self.options["--history"]:
        break
      
      # Get difference between last added element date and current file date
      previous_date = history_files[-1]["date"]
      date = f["date"]
      diff = date - previous_date

      if abs(diff.days) >= self.options["--history-gap"]:
        history_files.append(f)
        self.dates.append(f["date"])

    return history_files

  def handle_exception(self, e, message=""):
    """ Function handling exception for the current class """
    if self.options["--verbose"]:
      print(e)

    if message:
      ColorPrint.red(message)

  def kpi_process(self, kpi):
    """ Target process to deal with url data """
    kpi_data = []

    kpi_controls = DataFilter.gen_from_dict(kpi["controls"])
    kpi_source = self.data_sources[kpi["perimeter"]]
    kpi_i = KPI(name=kpi["name"], perimeter=kpi["perimeter"], filters=kpi_controls, date=kpi_source["date"])

    print(f"\n{kpi_i.get_name()}")

    for s in kpi["scopes"]:
      # Build the scope to pass to the kpi
      sd = DataScope.merge_scopes(f"Build - {s['name']}", [ self.scopes[b] for b in s["build"] ])
      scope_i = DataScope(name=s["name"], perimeter=kpi_i.get_perimeter(), data=sd)

      # Pass the scope to the kpi and get conformity data
      kpi_i.set_input_data(scope_i)
      kpi_data.append(kpi_i.to_dictionary())
      kpi_i.print_value(prefix=f"=> {scope_i.get_name()}: ")

    return (kpi_i, kpi_data)

  def kpi_thread_loop(self):
    """ Run kpi thread loop """
    print("Generating KPIs...")
    with Pool(processes=5) as pool:
      for kpi_res in pool.imap_unordered(self.kpi_process, self.kpi_list):
        if self.options["--history"]:
          h = self.kpi_hist[kpi_res[0].get_name()]
          h.add_kpi(kpi=kpi_res[0])

        self.results.extend(kpi_res[1])

  def run(self):
    """ Run command method """
    if self.options["--history"]:
      self.options["--history"] = int(self.options["--history"])

      if self.options["--history-gap"]:
        self.options["--history-gap"] = int(self.options["--history-gap"])

      else:
        self.options["--history-gap"] = 1

      print(f"Building KPI history for the last {self.options['--history']} period(s) of {self.options['--history-gap']} day(s)")

      history_files = { k: self.build_file_history(self.config["data_sources"][k]) for k in self.config["data_sources"].keys() }

      self.kpi_hist = { k["name"]: KPIHistory(name=k["name"]) for k in self.kpi_list }

      for i in range(self.options["--history"]):

        sources_i = { k: history_files[k][i] for k in history_files.keys() }
        ColorPrint.blue(f"\n {self.dates[i].strftime('%Y-%m-%d')} ")

        self.set_data_sources(sources_i, rawPath=True)
        self.set_filters(self.config["filters"])
        self.set_scopes(self.config["scopes"])

        self.kpi_thread_loop()
      
      print(f"\nPrinting histories...")
      for h in self.kpi_hist.values():
        h.print_history()

    else:
      self.kpi_thread_loop()

    if self.options["--export-csv"] and len(self.results) > 0:
      export_csv(self.results, self.options["--export-csv"], delimiter='|')
