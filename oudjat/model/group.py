from typing import List, Dict, Union

from . import GenericIdentifiable

class Group(GenericIdentifiable):
  """  """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(
    self,
    id: Union[int, str],
    name: str,
    label: str = None,
    description: str = None,
  ):
    """ Constructor """

    super().__init__(id=id, name=name, label=label, description=description)


  # ****************************************************************
  # Methods