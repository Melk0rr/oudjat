from typing import Dict, Union, List

from oudjat.model.assets import AssetType

class Location:
  """ A class to describe generic location with subnets, assets, users """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(
    self,
    id: str,
    name: str,
    description: str,
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
    
  def addAsset(asset: Asset, type: AssetType) -> None:
    """ Adds a new asset to the current location """
    