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

class KPI(DataScope):
  """ KPI class """
  print_colors = {
    "CONFORM": ColorPrint.green,
    "PARTIALLYCONFORM": ColorPrint.yellow,
    "NOTCONFORM": ColorPrint.red,
  }

  def __init__(
    self,
    name: str,
    perimeter: str,
    data: List[Dict] | DataScope,
    filters: List[Dict] | List[DataFilter] = [],
    description: str = "",
    date: datetime = None
  ):
    """ Constructor """
    super().__init__(name=name, data=data, filters=filters, description=description)
    self.conformity_level = None

    if date is None:
      date = datetime.today()

    self.date = date

  def get_conformity_level(self):
    """ Establish the conformity level """
    k_value = self.get_kpi_value()
    self.conformity_level = next(filter(lambda lvl: lvl.value["min"] <= k_value <= lvl.value["max"], list(ConformityLevel)))

    return self.conformity_level

  def get_kpi_value(self):
    """ Returns the percentage of conform data based on kpi control """
    if self.data is None:
      self.filter_data()

    return round(len(self.data) / len(self.data_in) * 100, 2)

  def print_value(self, prefix: str = ""):
    """ Print value with color based on kpi level """
    scope_str = self.to_string()

    print(f"{prefix}{scope_str[0]}", end=" = ")
    self.print_colors[self.conformity_level.name](f"{scope_str[1]}%")

  def to_dictionary(self):
    """ Converts the current instance into a dictionary """
    k_value = self.get_kpi_value()

    return {
      "name": self.name,
      "perimeter": self.perimeter,
      "scope": self.initial_scope,
      "scope_size": len(self.data_in),
      "conform_elements": len(self.data),
      "value": k_value,
      "date": self.date.strftime('%Y-%m-%d')
    }

  def to_string(self):
    """ Converts the current instance into a string """
    k_value = self.get_kpi_value()
    return (f"{len(self.data)} / {len(self.data_in)}", f"{k_value}")