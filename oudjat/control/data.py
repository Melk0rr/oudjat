""" Data module handling various data manipulation aspects """
from typing import List, Dict

class DataFilter:
  """ DataFilter class : handling data filtering """

  def __init__(self, fieldname: str, value: List[str | int | float]):
    """ Constructor """
    self.fieldname = fieldname
    self.value = value

  def check_filter(self, element: Dict) -> bool:
    """ Returns whether or not the element match the filter """
    return element[self.fieldname] in self.value

  @staticmethod
  def filter_data(data_to_filter: List[Dict], filters: List):
    filtered_data = []
    for el in data_to_filter:
      conditions = [ f.check_filter(el) for f in filters ]
      if False not in conditions:
        filtered_data.append(el)

    return filtered_data

class DataScope:
  """ DataScope class : handling data unfiltered and filtered state """

  def __init__(self, name: str, data: List[Dict], filters: List[DataFilter] = []):
    """ Constructor """
    self.name = name
    self.data_in = data.get_data_out() if isinstance(data, DataScope) else data

    self.filters = filters
    self.data_out = None

  def get_name(self):
    """ Getter for perimeter name """
    return self.name

  def get_data_in(self):
    """ Returns the inital data before filters are applied """
    return self.data_in

  def filter_data(self):
    """ Apply filters to kpi data to get perimeter specific data """

    self.data_out = self.data_in

    if len(self.filters) > 0:
      self.data_out = DataFilter.filter_data(self.data_in, self.filters)

  def get_data_out(self):
    """ Getter for perimeter data """
    if self.data_out is None:
      self.filter_data()

    return self.data_out