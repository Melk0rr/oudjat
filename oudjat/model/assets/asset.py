from typing import List, Dict, Union, Any

from oudjat.utils import ColorPrint
from oudjat.model import GenericIdentifiable

from . import AssetType

class Asset(GenericIdentifiable):
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
    location: Union["Location", List["Location"]] = None
  ):
    """ Constructor """

    super().__init__(id=id, name=name, label=label, description=desctiption)

    self.location = []
    self.set_location(location)

    self.asset_type = asset_type
    self.location = location
    self.custom_attributes = {}

  # ****************************************************************
  # Methods

  def get_location(self) -> Union["Location", List["Location"]]:
    """ Getter for the asset location """
    return self.location

  def get_asset_type(self) -> AssetType:
    """ Getter for asset type """
    return self.asset_type
  
  def get_custom_attr(self, key: str = None) -> Any:
    """ Getter for custom attributes """
    if key is None:
      return self.custom_attributes
    
    return self.custom_attributes[key]
  
  def set_custom_attr(self, new_custom_attr: Dict[str, Any]) -> None:
    """ Setter for custom attributes """
    self.custom_attributes = new_custom_attr
    
  def add_custom_attr(self, key: str, value: Any) -> None:
    """ Adds a new custom attribute """
    self.custom_attributes[key] = value
    
  def add_multiple_custom_attr(self, new_custom_attr: Dict[str, Any]) -> None:
    """ Adds multiple new custom attributes """
    self.custom_attributes.update(new_custom_attr)
    
  def del_custom_attr(self, key: str) -> None:
    """ Deletes a custom attribute by key """
    del self.custom_attributes[key]
    
  def clear_custom_attr(self) -> None:
    """ Clears custom attributes """
    self.custom_attributes = {}
  
  def set_location(
    self,
    location: Union["Location", List["Location"]]
  ) -> None:
    """ Setter for asset location """

    if not isinstance(location, list):
      location = [ location ]

    new_location = []    
    
    for l in location:
      if type(l).__name__ == "Location":
        new_location.append(l)
        
    self.location = new_location
  
  def to_dict(self) -> Dict:
    """ Converts current asset into a dict """

    return {
      **super().to_dict(),
      "asset_type": self.asset_type.name,
      "location": self.location
      **self.custom_attributes
    }