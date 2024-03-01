""" DataFilter module handling data filtering """
from typing import List, Dict


class DataFilter:
  """ DataFilter class """

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