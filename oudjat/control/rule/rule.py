from typing import List, Dict, Union

from oudjat.control.data.data_filter import DataFilter
from oudjat.control.risk.risk import Risk

class Rule:
  """ A class to describes rules """
  
  # ****************************************************************
  # Attributes & Constructors
  def __init__(
    self,
    id: str,
    name: str,
    description: str,
    associatedRisks: List[Risk] = None,
    filters: Union[List[DataFilter], List[Dict]] = None
  ):
    """ Constructor """
    self.id = id
    self.name = name
    seld.description = description

    

  # ****************************************************************
  # Methods

  # ****************************************************************
  # Static methods
