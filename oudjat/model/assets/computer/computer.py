from oudjat.model.assets import Asset
from . import ComputerType

class Computer(Asset):
  """ A common class for computers """

  def __init__(
    self,
    id: str,
    name: str
  ):
    """ Constructor """
    
