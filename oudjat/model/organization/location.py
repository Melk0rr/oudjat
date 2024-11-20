from typing import Union, List

from oudjat.model.assets import AssetType, Asset
from oudjat.model.assets.network import Subnet

class Location:
  """ A class to describe generic location with subnets, assets, users """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(
    self,
    id: str,
    name: str,
    description: str,
    city: str = None,
    label: str = None,
    subnet: Union[Subnet, List[Subnet]] = None
  ):
    """ Constructor """
    self.id = id
    self.name = name
    self.label = label
    self.description = description
    
    self.assets = {}

  # ****************************************************************
  # Methods
    
  def add_asset(asset: Asset, asset_type: AssetType) -> None:
    """ Adds a new asset to the current location """

    if asset_type not in self.assets.keys():
      self.assets[asset_type] = {}

    if asset.get_id() not in self.assets.keys():
      self.assets[asset_type][asset.get_id()] = asset
    