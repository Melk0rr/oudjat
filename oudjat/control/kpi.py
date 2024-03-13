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

  def __init__(
    self,
    name: str,
    perimeter: str,
    data: DataScope | List[Dict],
    kpi_dictionnaries: List[Dict],
    filters: List[Dict] | List[DataFilter],
    description: str = ""
  ):
    """ Constructor """
    self.name = name
    self.perimeter = perimeter
    self.data = data if isinstance(data, DataScope) else DataScope(perimeter, data)
    self.description = description
    self.group_filters = DataFilter.get_valid_filters_list(filters)

    self.kpis = []
    for k in kpi_dictionnaries:
      kpi = KPI(name=k["name"], perimeter=self.perimeter, data=k["data"], filters=self.group_filters, description=k.get("description", ""))
      self.kpis.append(kpi)
  
  def get_name(self):
    """ Getter for kpi name """
    return self.name

  def get_kpis_data(self):
    """ Get kpis dictionnary """
    k_data = []
    for k in self.kpis:
      d = k.to_dictionary()
      d.update({ "group": self.name })
      k_data.append(d)

    return k_data

  def print_values(self):
    """ Print KPI results """
    print(f"\n{self.name}")
    for s in self.scopes:
      s.print_value()


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
    self.filter_data()
    self.conformity_level = self.get_conformity_level()

    if date is None:
      date = datetime.today()

    self.date = date

  def get_conformity_level(self):
    """ Establish the conformity level """
    return next(filter(lambda lvl: lvl.value["min"] <= self.get_kpi_value() <= lvl.value["max"], list(ConformityLevel)))

  def get_kpi_value(self):
    """ Returns the percentage of conform data based on kpi control """
    return round(len(self.data) / len(self.data_in) * 100, 2)

  def print_value(self, prefix: str = ""):
    """ Print value with color based on kpi level """
    scope_str = self.to_string()

    print(f"{prefix}{scope_str[0]}", end=" = ")
    self.print_colors[self.conformity_level.name](f"{scope_str[1]}%")

  def to_dictionary(self):
    """ Converts the current instance into a dictionary """
    return {
      "name": self.name,
      "perimeter": self.perimeter,
      "scope": self.initial_scope,
      "scope_size": len(self.data_in),
      "conform_elements": len(self.data),
      "value": self.get_kpi_value(),
      "date": self.date.strftime('%Y-%m-%d')
    }

  def to_string(self):
    """ Converts the current instance into a string """
    return (f"{self.name}: {len(self.data)} / {len(self.data_in)}", f"{self.get_kpi_value()}")