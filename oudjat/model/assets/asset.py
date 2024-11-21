from __future__ import annotations

from typing import List, Dict, Union

import oudjat.model.organization

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
    location: Union[oudjat.model.organization.Location, List[oudjat.model.organization.Location]] = None
  ):
    """ Constructor """

    super().__init__(id=id, name=name, label=label, description=desctiption)

    self.location = []
    self.set_location(location)

    self.asset_type = asset_type
    self.location = location

  # ****************************************************************
  # Methods

  def get_location(self) -> Union[oudjat.model.organization.Location, List[oudjat.model.organization.Location]]:
    """ Getter for the asset location """
    return self.location

  def get_asset_type(self) -> AssetType:
    """ Getter for asset type """
    return self.asset_type
  
  def set_location(
    self,
    location: Union[oudjat.model.organization.Location, List[oudjat.model.organization.Location]]
  ) -> None:
    """ Setter for asset location """

    if not isinstance(location, list):
      location = [ location ]

    new_location = []    
    
    for l in location:
      if isinstance(l, oudjat.model.organization.Location):
        new_location.append(l)
        
    self.location = new_location
  
  def to_dict(self) -> Dict:
    """ Converts current asset into a dict """

    return {
      **super().to_dict(),
      "asset_type": self.asset_type.name,
      "location": self.location
    }