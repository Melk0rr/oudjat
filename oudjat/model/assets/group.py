from typing import List, Dict, Union

from . import Asset

class GroupMemberList(dict):
  """ Dict override to handle member list """

class Group(Asset):
  """  """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(
    self,
    id: Union[int, str],
    name: str,
    label: str = None,
    description: str = None,
  ):
    """ Constructor """

    super().__init__(id=id, name=name, label=label, description=description)

    self.members = GroupMemberList()
    
  # ****************************************************************
  # Methods

  def __str__(self) -> str:
    """ Converts the current instance into a string """
    return f"{self.name}"