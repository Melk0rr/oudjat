from typing import Dict, Union

from oudjat.model.organization import Location

from . import AssetType

class Asset:
  """ Generic asset class to be inherited by all model asset types """

  # ****************************************************************
  # Attributes & Constructors
  
  def __init__(
    self,
    id: Union[int, str],
    name: str,
    asset_type: AssetType,
    label: str = None,
    desctiption: str = None,
    location: Location = None
  ):
    """ Constructor """

    self.id = id
    self.name = name
    self.label = label
    self.desctiption = desctiption
    self.location = location
    self.asset_type = asset_type

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

  def get_location(self) -> Location:
    """ Getter for the asset location """
    return self.location

  def get_asset_type(self) -> AssetType:
    """ Getter for asset type """
    return self.asset_type
  
  def set_location(self, location: Location) -> None:
    """ Setter for asset location """
    
    if isinstance(location, Location):
      self.location = location
  
  def to_dict(self) -> Dict:
    """ Converts current asset into a dict """
    return {
      "id": self.id,
      "name": self.name,
      "label": self.label,
      "description": self.desctiption,
      "type": self.asset_type.name
    }