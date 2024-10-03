from typing import List, Dict, Union, Any

from oudjat.utils import ColorPrint
from oudjat.control.data import DataFilterOperations

class DataFilter:
  """ DataFilter class : handling data filtering """

  def __init__(
    self,
    fieldname: str,
    value: Union[Any, List[Any]],
    operator: str = "in"
  ):
    """ Constructor """
    if operator not in DataFilterOperations.keys():
      raise ValueError(f"Invalid operator provided: {operator}")

    self.fieldname = fieldname
    self.operator = operator
    self.value = value

    self.operation = DataFilterOperations[self.operator]

  def check_filter(self, element: Dict) -> bool:
    """ Returns whether or not the element match the filter """
    return self.operation[self.operator](element[self.fieldname], self.value)
  
  def to_string(self) -> str:
    """ Converts the current instance into a string """
    return f"{self.fieldname} {self.operator} {self.value}"
  
  @staticmethod
  def datafilter_from_dict(dictionnary: Dict) -> "DataFilter":
    """ Converts a dictionary """
    return DataFilter(
      fieldname=dictionnary["field"],
      operator=dictionnary.get("operator", "in"),
      value=dictionnary["value"]
    )

  @staticmethod
  def get_valid_filters_list(
    filters_list: Union[List[Dict], List["DataFilter"]]
  ) -> List["DataFilter"]:
    """ Check filters type and format them into DataFilter instances if needed """
    filters = []

    for f in filters_list:
      # Checks if the current filter is either a dictionary or a DataFilter instance
      if not isinstance(f, DataFilter) and not isinstance(f, dict):
        ColorPrint.yellow(f"Invalid filter: {f}")
        continue

      filter_i = f
      if isinstance(f, dict):
        filter_i = DataFilter.datafilter_from_dict(f)
      
      filters.append(filter_i)

    return filters

  @staticmethod
  def gen_from_dict(filters: List[Dict]) -> List["DataFilter"]:
    """ Generates DataFitler instances based on dictionnaries """
    filter_instances = []

    for f in filters:
      current_filter = DataFilter.datafilter_from_dict(f)
      filter_instances.append(current_filter)

    return filter_instances

  @staticmethod
  def get_conditions(element: Any, filters: Union[List["DataFilter"], List[Dict]]) -> bool:
    """ Checks given filters on provided element """
    checks = []

    for f in filters:
      if isinstance(f, DataFilter):
        checks.append(f.check_filter(element))
      
      else:
        operation = DataFilterOperations[f["operator"]]
        checks.append(operation(element[f["fieldname"]], f["value"]))
      
    return all(checks)

  @staticmethod
  def filter_data(data_to_filter: List[Dict], filters: List["DataFilter"]) -> List[Dict]:
    """ Filters data based on given filters """
    filtered_data = []
    for el in data_to_filter:
      conditions = all(f.check_filter(el) for f in filters)
      if conditions:
        filtered_data.append(el)

    return filtered_data