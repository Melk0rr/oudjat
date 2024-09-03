from oudjat.model.asset import Asset
from oudjat.model.computer_type import ComputerType

class Computer(Asset):
  """ A common class for computers """

  def __init__(
    self,
    id: str,
    name: str
  ):
    """ Constructor """
    
