from typing import Dict, Union

class GenericIdentifiable:
  """ Generic class for objects with common attributes like id, name, description and label """

  # ****************************************************************
  # Attributes & Constructors
  
  def __init__(
    self,
    id: Union[int, str],
    name: str,
    label: str = None,
    desctiption: str = None,
  ):
    """ Constructor """

    self.id = id
    self.name = name
    self.label = label
    self.desctiption = desctiption

  # ****************************************************************
  # Methods

  def get_id(self) -> Union[int, str]:
    """ Getter for instance id """
    return self.id

  def get_name(self) -> str:
    """ Getter for instance name """
    return self.name

  def get_label(self) -> str:
    """ Getter for instance label """
    return self.label

  def get_description(self) -> str:
    """ Getter for instance description """
    return self.desctiption
  
  def set_description(self) -> None:
    """ Setter for instance description """

  def __str__(self) -> str:
    """ Converts the current instance into a string """
    raise NotImplementedError(
        "__str__() method must be implemented by the overloading class")

  def to_dict(self) -> Dict:
    """ Converts the current instance into a dictionary """
    return {
      "id": self.id,
      "name": self.name,
      "label": self.label,
      "description": self.desctiption
    }