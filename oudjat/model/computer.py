from oudjat.model import Asset
from oudjat.model import ComputerType

class Computer(Asset):
  """ A common class for computers """

  def __init__(
    self,
    id: str,
    name: str
  ):
    """ Constructor """
    
