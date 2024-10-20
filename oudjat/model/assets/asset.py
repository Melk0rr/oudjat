from typing import Dict, Union

from . import AssetType

class Asset:
  """ Generic asset class to be inherited by all model asset types """

  # ****************************************************************
  # Attributes & Constructors
  
  def __init__(
    self,
    id: Union[int, str],
    name: str,
    label: str,
    type: AssetType,
    desctiption: str = None
  ):
    """ Constructor """

    self.id = id
    self.name = name
    self.label = label
    self.desctiption = desctiption
    self.type = type

  # ****************************************************************
  # Methods

  def get_id(self) -> Union[int, str]:
    """ Getter for asset id """
    return self.id

  def get_name(self) -> str:
    """ Getter for asset name """
    return self.name

  def get_label(self) -> str:
    """ Getter for asset label """
    return self.label

  def get_description(self) -> str:
    """ Getter for asset description """
    return self.desctiption

  def get_type(self) -> AssetType:
    """ Getter for asset type """
    return self.type
  
  def to_dict(self) -> Dict:
    """ Converts current asset into a dict """
    return {
      "id": self.id,
      "name": self.name,
      "label": self.label,
      "description": self.desctiption,
      "type": self.type.name
    }