from oudjat.model.asset_type import AssetType

class Asset:
  """ Generic asset class to be inherited by all model asset types """

  # ****************************************************************
  # Attributes & Constructors
  
  def __init__(
    self,
    id: str,
    name: str,
    type: AssetType,
    desctiption: str = None
  ):
    """ Constructor """

    self.id = id
    self.name = name
    self.desctiption = desctiption
    self.type = type

  # ****************************************************************
  # Methods
  
  