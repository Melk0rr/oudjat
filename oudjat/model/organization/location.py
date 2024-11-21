from typing import Union, List

from oudjat.model import GenericIdentifiable
from oudjat.model.assets import AssetType, Asset
from oudjat.model.assets.network import Subnet

class Location(GenericIdentifiable):
  """ A class to describe generic location with subnets, assets, users """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(
    self,
    id: Union[int, str],
    name: str,
    description: str,
    city: str = None,
    label: str = None,
    subnet: Union[Subnet, List[Subnet]] = None
  ):
    """ Constructor """
    super().__init__(id=id, name=name, label=label, description=description)
    
    self.assets = {}

    if not isinstance(subnet, list):
      subnet = [ subnet ]
      
    self.subnet = subnet

  # ****************************************************************
  # Methods

  def get_subnet(self) -> Subnet:
    """ Getter for the location subnet """
    return self.subnet

  def add_subnet(self, subnet: Subnet) -> None:
    """ Adds a new subnet to the location """
    
    if not isinstance(subnet, Subnet):
      raise ValueError("Location.add_subnet::Invalid subnet provided")

    self.subnet.append(subnet)

  def get_asset(self, asset_type: AssetType, asset_id: Union[int, str]) -> Asset:
    """ Looks for an asset based on asset type and id """
    return self.assets.get(asset_type, {}).get(asset_id, None)
  
  def get_asset_per_type(self, asset_type: Union[str, AssetType]) -> Dict:
    """ Returns a dictionary of assets for the given type """
    
    if isinstance(asset_type, AssetType):
      asset_type = asset_type.name
      
    if asset_type not in AssetType._member_names_:
      raise ValueError(f"Location.get_asset_per_type::Invalid asset type provided: {asset_type}")

    if asset_type not in self.assets.keys():
      return None
    
    return self.assets[asset_type]
  
  def add_asset(asset: Asset, asset_type: AssetType) -> None:
    """ Adds a new asset to the current location """

    if asset_type not in self.assets.keys():
      self.assets[asset_type] = {}

    if asset.get_id() not in self.assets.keys():
      self.assets[asset_type][asset.get_id()] = asset
    

class LocationGroup(GenericIdentifiable):
  """ A class to handle multiple locations as groups """
  
  # ****************************************************************
  # Attributes & Constructors

  def __init__(
    self,
    id: Union[int, str],
    name: str,
    description: str,
    label: str = None,
  ):
    """ Constructor """
    super().__init__(id=id, name=name, label=label, description=description)
    
    self.locations = {}

  # ****************************************************************
  # Methods
  
  def get_location(self, location_id: Union[int, str]) -> Location:
    """ Returns a location based on its id """
    return self.locations.get(location_id, None)
  
  def add_location(self, location: Location) -> None:
    """ Adds a location to the current group """
    
    if location.get_id() not in self.locations.keys():
      self.locations[location.get_id()] = location
      
  def remove_location(self, location_id: Union[int, str]) -> None:
    """ Removes a location from the group """
    
    if location_id in self.locations.keys():
      del self.locations[location_id]