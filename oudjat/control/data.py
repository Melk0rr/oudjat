""" Data module handling various data manipulation aspects """
from typing import List, Dict, Union, Any

from oudjat.utils.color_print import ColorPrint

def ope_contains(v: Any, t: Any) -> bool:
  """ Checks whether or not the target value contains the value (v) """
  return v.contains(t)
    
def ope_in(v: Any, t: Any) -> bool:
  """ Checks whether or not the value (v) to check is 'in' the target value """
  return v in t

class DataFilter:
  """ DataFilter class : handling data filtering """

  operations = {
    "contains": ope_contains,
    "in": ope_in
  }

  def __init__(
    self,
    fieldname: str,
    value: Union[Any, List[Any]],
    operator: str = "in"
  ):
    """ Constructor """
    self.fieldname = fieldname
    self.operator = operator
    self.value = value

  def check_filter(self, element: Dict) -> bool:
    """ Returns whether or not the element match the filter """
    return self.operations[self.operator](element[self.fieldname], self.value)
  
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
      
      filters.append(f)

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
  def filter_data(data_to_filter: List[Dict], filters: List["DataFilter"]) -> List[Dict]:
    """ Filters data based on given filters """
    filtered_data = []
    for el in data_to_filter:
      conditions = all(f.check_filter(el) for f in filters)
      if conditions:
        filtered_data.append(el)

    return filtered_data

class DataScope:
  """ DataScope class : handling data unfiltered and filtered state """

  def __init__(
    self,
    name: str,
    perimeter: str,
    scope: Union[List[Dict], "DataScope"] = None,
    filters: Union[List[Dict], List["DataFilter"]] = [],
    description: str = None
  ):
    """ Constructor """
    self.name = name
    self.description = description
    self.perimeter = perimeter

    self.initial_scope = scope

    self.filters = DataFilter.get_valid_filters_list(filters)

  def get_name(self) -> str:
    """ Getter for perimeter name """
    return self.name

  def get_initial_scope(self) -> Union[List[Dict], "DataScope"]:
    """ Getter for parent scope """
    return self.initial_scope
  
  def get_initial_scope_name(self) -> str:
    """ Getter for initial scope name """
    return self.initial_scope.get_name() if isinstance(self.initial_scope, DataScope) else None

  def get_input_data(self) -> List[Dict]:
    """ Getter for input data """
    return self.initial_scope.get_data() if isinstance(self.initial_scope, DataScope) else self.initial_scope

  def get_perimeter(self) -> str:
    """ Getter for perimeter """
    return self.perimeter

  def set_initial_scope(self, scope: Union[List[Dict], "DataScope"]) -> None:
    """ Setter for input data """
    self.initial_scope = scope 

  def set_filters(self, filters: Union[List[Dict], List[DataFilter]] = []) -> None:
    """ Setter for filters """
    self.filters = DataFilter.get_valid_filters_list(filters)

  def get_data(self) -> List[Dict]:
    """ Getter for perimeter data """
    if self.initial_scope is None:
      raise ValueError(f"{__class__}: no parent scope defined for the current scope {self.name}")

    data = self.get_input_data()

    if len(self.filters) > 0:
      data = DataFilter.filter_data(data, self.filters)

    return data

  @staticmethod
  def merge_scopes(name: str, scopes: List["DataScope"]) -> "DataScope":
    """ Merges given scopes into one """
    # Check if all scopes are on the same perimeter
    perimeters = set([ s.get_perimeter() for s in scopes ])
    if len(perimeters) > 1:
      raise ValueError(f"{__class__}: Error merging scopes. Please provide scopes with the same perimeter")

    merge_data = []
    for s in scopes:
      merge_data.extend(s.get_data())

    merge = DataScope(name=name, perimeter=list(perimeters)[0], scope=merge_data, filters=[])

    return merge