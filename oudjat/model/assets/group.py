from typing import List, Dict, Union

from . import Asset

class GroupMemberList(dict):
  """ Dict override to handle member list """

  def 

class Group(Asset):
  """ A class to handle groups of assets """

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

  def add_member(self, member: Asset) -> None:
    """ Adds a new member to the member list """
    if isinstance(member, Asset):
      self.members[member.get_id()] = member

  def __str__(self) -> str:
    """ Converts the current instance into a string """
    return f"{self.name}"