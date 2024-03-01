""" DataScope module handling data perimeters based on data filters """
from typing import List, Dict

from kpicalculator.kpi.data_filter import DataFilter

class DataScope:
  """ DataPerimeter class """

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