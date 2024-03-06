""" KPI module handling operations related to indicators """
from datetime import datetime
from typing import List, Dict
from enum import Enum

from oudjat.utils.color_print import ColorPrint
from oudjat.control.data import DataFilter, DataScope

class ConformityLevel(Enum):
  """ Defines the levels of conformity for a KPI or any other related element """
  CONFORM = { "min": 95, "max": 100.01 }
  PARTIALLYCONFORM = { "min": 70, "max": 95 }
  NOTCONFORM = { "min": 0, "max": 70 }


class KPIGroup:
  """ KPIGroup class : grouping KPI by perimeter and controls """

  def __init__(self, kpi_dict: Dict, data_source: List[Dict], date: datetime = None):
    """ Constructor """
    self.data_source = DataScope(kpi_dict["perimeter"], data_source)
    self.name = kpi_dict["name"]

    if date is None:
      date = datetime.today()

    self.date = date

    self.kpis = []
    for s in kpi_dict["scopes"]:
      filters = [ DataFilter(f["name"], f["value"]) for f in s["fields"] ]
      scope_data = DataScope(s["name"], self.data_source, filters=filters)
      scope_data.filter_data()

      kpi = KPI(self, scope_data)
      self.kpis.append(kpi)

    self.controls = [ DataFilter(ctrl["name"], ctrl["value"]) for ctrl in kpi_dict["controls"] ]
  
  def get_name(self):
    """ Getter for kpi name """
    return self.name

  def get_data_source(self):
    """ Getter for kpi data source """
    return self.data_source

  def get_controls(self):
    """ Getter for kpi filters """
    return self.controls

  def get_date(self):
    """ Returns the kpi date """
    return self.date

  def get_values(self):
    """ Calculates kpi values for all perimeters """
    return [ s.to_dictionary() for s in self.scopes ]

  def print_values(self):
    """ Print KPI results """
    print(f"\n{self.name}")
    for s in self.scopes:
      s.print_value()


class KPI:
  """ KPI class """
  print_colors = {
    "CONFORM": ColorPrint.green,
    "PARTIALLYCONFORM": ColorPrint.yellow,
    "NOTCONFORM": ColorPrint.red,
  }

  def __init__(self, group: KPIGroup, data_scope: DataScope):
    """ Constructor """
    self.group = group
    self.data_scope = data_scope
    self.conform_data = None

  def get_name(self):
    """ Getter for KPI name """
    return (f"{self.group.get_name()}_{self.data_scope.get_name()}").lower()

  def get_scope_name(self):
    """ Getter for current scope name """
    return self.data_scope.get_name()

  def get_full_name(self):
    """ Get KPIScope name based on kpi name and data scope name """
    return f"{self.group.get_name()} - {self.data_scope.get_name()}"

  def get_conform_scope(self):
    """ Apply kpi controls to scope data to get conform data elements """
    if self.conform_data is None:
      self.conform_data = DataScope(self.get_full_name() + " > OK", self.data_scope, self.group.get_controls())
      self.conform_data.filter_data()

    return self.conform_data

  def get_kpi_value(self):
    """ Returns the percentage of conform data based on kpi control """
    return round(len(self.get_conform_scope().get_data_out()) / len(self.data_scope.get_data_out()) * 100, 2)

  def print_value(self):
    """ Print value with color based on kpi level """
    kpi_level = next(filter(lambda lvl: lvl.value["min"] <= self.get_kpi_value() <= lvl.value["max"], list(ConformityLevel)))

    scope_str = self.to_string()
    print(f"=> {scope_str[0]}", end=" = ")
    self.print_colors[kpi_level.name](f"{scope_str[1]}%")

  def to_dictionary(self):
    """ Converts the current instance into a dictionary """
    return {
      "name": self.get_name(),
      "group": self.group.get_name(),
      "perimeter": self.group.get_data_source().get_name(),
      "scope": self.data_scope.get_name(),
      "scope_size": len(self.data_scope.get_data_out()),
      "conform_elements": len(self.get_conform_scope().get_data_out()),
      "kpi_value": self.get_kpi_value(),
      "date": self.group.get_date().strftime('%Y-%m-%d')
    }

  def to_string(self):
    """ Converts the current instance into a string """
    return (f"{self.get_scope_name()}: {len(self.get_conform_scope().get_data_out())} / {len(self.data_scope.get_data_out())}", f"{self.get_kpi_value()}")