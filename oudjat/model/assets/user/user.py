from typing import List, Dict

from oudjat.model.assets import Asset, AssetType

class User(Asset):
  """ A common class for users """

  # ****************************************************************
  # Attributes & Constructor

  def __init__(
    self,
    id: Union[int, str],
    name: str,
    label: str = None,
    description: str = None,
  ):
    """ Constructor """

    super().__init__(id=id, name=name, label=label, desctiption=description, type=AssetType.USER)

  # ****************************************************************
  # Methods