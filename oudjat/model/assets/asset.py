from oudjat.model.asset_type import AssetType

class Asset:
  """ Generic asset class to be inherited by all model asset types """

  def __init__(
    self,
    id: str,
    name: str,
    type: AssetType
  ):
    """ Constructor """

    self.id = id
    self.name = name
    self.type = type
