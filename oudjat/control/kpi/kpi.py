""" KPI module handling operations related to indicators """
from datetime import datetime
from typing import List, Dict, Tuple 
from enum import Enum

from oudjat.utils import ColorPrint
from oudjat.control.data import DataScope
from oudjat.control.data import DataFilter

class ConformityLevel(Enum):
  """ Defines the levels of conformity for a KPI or any other related element """
  CONFORM = { "min": 95, "max": 100.01, "color": ColorPrint.green }
  PARTIALLYCONFORM = { "min": 70, "max": 95, "color": ColorPrint.yellow }
  NOTCONFORM = { "min": 0, "max": 70, "color": ColorPrint.red }
      

class KPI(DataScope):
  """ KPI class """

  def __init__(
    self,
    name: str,
    perimeter: str,
    scope: List[Dict] | DataScope = None,
    filters: List[Dict] | List[DataFilter] = [],
    description: str = None,
    date: datetime = None
  ):
    """ Constructor """
    super().__init__(name=name, perimeter=perimeter, scope=scope, filters=filters, description=description)

    if date is None:
      date = datetime.today()

    self.date: datetime = date

  def get_date(self) -> datetime:
    """ Getter for kpi date """
    return self.date

  def get_conformity_level(self, value: float = None) -> "ConformityLevel":
    """ Establish the conformity level """
    if value is None:
      value = self.get_kpi_value()
    return next(filter(lambda lvl: lvl.value["min"] <= value <= lvl.value["max"], list(ConformityLevel)))

  def get_kpi_value(self) -> float:
    """ Returns the percentage of conform data based on kpi control """
    return round(len(self.get_data()) / len(self.get_input_data()) * 100, 2)

  def get_print_function(self) -> object:
    """ Defines print function """
    return self.get_conformity_level().value["color"]

  def print_value(
    self,
    prefix: str = None,
    suffix: str = "%\n",
    print_details: bool = True
  ) -> None:
    """ Print value with color based on kpi level """
    scope_str = self.to_string()

    print(prefix, end="")
    if print_details:
      print(f"{scope_str[0]}", end=" = ")

    self.get_print_function()(f"{scope_str[1]}", end=f"{suffix}")

  def get_date_str(self) -> str:
    """ Returns formated date string """
    return self.date.strftime('%Y-%m-%d')

  def to_dictionary(self) -> Dict:
    """ Converts the current instance into a dictionary """
    k_value = self.get_kpi_value()
    conformity = self.get_conformity_level(k_value)

    return {
      "name": self.name,
      "perimeter": self.perimeter,
      "scope": self.get_initial_scope_name(),
      "scope_size": len(self.get_input_data()),
      "conform_elements": len(self.get_data()),
      "value": k_value,
      "conformity": conformity.name,
      "date": self.get_date_str()
    }

  def to_string(self) -> Tuple[str, str]:
    """ Converts the current instance into a string """
    k_value = self.get_kpi_value()
    return (f"{len(self.get_data())} / {len(self.get_input_data())}", f"{k_value}")
