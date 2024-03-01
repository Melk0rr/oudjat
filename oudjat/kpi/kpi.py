""" KPI module handling operations related to indicators """
from datetime import datetime
from typing import List, Dict

from kpicalculator.utils.color_print import ColorPrint
from kpicalculator.kpi.data_filter import DataFilter
from kpicalculator.kpi.data_scope import DataScope

class KPILevel:
  """ KPILevel class : level of conformity of a KPI """

  def __init__(self, name: str, min: float, max: float, color: str = "white"):
    """ Constructor """
    self.name = name
    self.min = min
    self.max = max
    self.color = color

  def get_name(self):
    """ Getter for level name """
    return self.name

  def get_min(self):
    """ Getter for level minimum value """
    return self.min

  def get_max(self):
    """ Getter for level masimum value """
    return self.max

  def get_color(self):
    """ Getter for level color """
    return self.color


class KPI:
  """ KPI class """

  def __init__(self, kpi_dict: Dict, data_source: List[Dict], date: datetime = None):
    """ Constructor """
    self.data_source = DataScope(kpi_dict["perimeter"], data_source)
    self.name = kpi_dict["name"]

    if date is None:
      date = datetime.today()

    self.date = date

    self.scopes = []
    for s in kpi_dict["scopes"]:
      filters = [ DataFilter(f["name"], f["value"]) for f in s["fields"] ]
      scope_data = DataScope(s["name"], self.data_source, filters=filters)
      scope_data.filter_data()

      kpi_scope = KPIScope(self, scope_data)
      self.scopes.append(kpi_scope)

    self.controls = [ DataFilter(ctrl["name"], ctrl["value"]) for ctrl in kpi_dict["controls"] ]
    self.levels = [ KPILevel(k, lvl["min"], lvl["max"], lvl["color"]) for k, lvl in kpi_dict["levels"].items() ]
  
  def get_name(self):
    """ Getter for kpi name """
    return self.name

  def get_data_source(self):
    """ Getter for kpi data source """
    return self.data_source

  def get_controls(self):
    """ Getter for kpi filters """
    return self.controls

  def get_levels(self):
    """ Getter for kpi levels """
    return self.levels

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


class KPIScope:
  print_colors = {
    "green": ColorPrint.green,
    "yellow": ColorPrint.yellow,
    "red": ColorPrint.red,
    "white": ColorPrint.white,
  }

  def __init__(self, kpi: KPI, data_scope: DataScope):
    """ Constructor """
    self.kpi = kpi
    self.data_scope = data_scope
    self.conform_data = None

  def get_scope_name(self):
    """ Getter for current scope name """
    return self.data_scope.get_name()

  def get_full_name(self):
    """ Get KPIScope name based on kpi name and data scope name """
    return f"{self.kpi.get_name()} - {self.data_scope.get_name()}"

  def get_conform_scope(self):
    """ Apply kpi controls to scope data to get conform data elements """
    if self.conform_data is None:
      self.conform_data = DataScope(self.get_full_name() + " > OK", self.data_scope, self.kpi.get_controls())
      self.conform_data.filter_data()

    return self.conform_data

  def get_kpi_value(self):
    """ Returns the percentage of conform data based on kpi control """
    return round(len(self.get_conform_scope().get_data_out()) / len(self.data_scope.get_data_out()) * 100, 2)

  def print_value(self):
    """ Print value with color based on kpi level """
    kpi_level = next(filter(lambda lvl: lvl.get_min() <= self.get_kpi_value() <= lvl.get_max(), self.kpi.get_levels()))

    scope_str = self.to_string()
    print(f"=> {scope_str[0]}", end=" = ")
    self.print_colors[kpi_level.get_color()](f"{scope_str[1]}%")

  def to_dictionary(self):
    """ Converts the current instance into a dictionary """
    return {
      "name": (f"{self.kpi.get_name()}_{self.data_scope.get_name()}").lower(),
      "category": self.kpi.get_name(),
      "perimeter": self.kpi.get_data_source().get_name(),
      "scope": self.data_scope.get_name(),
      "scope_size": len(self.data_scope.get_data_out()),
      "conform_elements": len(self.get_conform_scope().get_data_out()),
      "kpi_value": self.get_kpi_value(),
      "date": self.kpi.get_date().strftime('%Y-%m-%d')
    }

  def to_string(self):
    """ Converts the current instance into a string """
    return (f"{self.get_scope_name()}: {len(self.get_conform_scope().get_data_out())} / {len(self.data_scope.get_data_out())}", f"{self.get_kpi_value()}")