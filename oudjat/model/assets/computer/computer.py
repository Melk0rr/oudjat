from oudjat.model.assets import Asset
from oudjat.model.assets.network import IPv4
from oudjat.model.assets.software import SoftwareRelease
from . import ComputerType

class Computer(Asset):
  """ A common class for computers """

  def __init__(
    self,
    id: str,
    name: str,
    os: SoftwareRelease = None,
    ip: List[IPv4] = None
  ):
    """ Constructor """
    
    self.id = id
    self.name = name
    
    self.os = os
    
    self.ip = ip
    self.softwares: List[SoftwareRelease] = []
    
    
    
