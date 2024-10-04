from typing import Dict, Union, List

class Location:
  """ A class to describe generic location with subnets, assets, users """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(
    self,
    id: str,
    name: str,
    desctiption: str,
    label: str = None,
    subnet: Union[Subnet, List[Subnet]] = None,
    users: List[User] = None,
    computers: List[Computer] = None,
    url: Union[URL, List[URL]] = None
  ):
    """ Constructor """
    self.id = id
    self.name = name
    
    self.assets = {}