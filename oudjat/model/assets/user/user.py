import re

from typing import List, Dict, Union

from oudjat.model.assets import Asset, AssetType

class User(Asset):
  """ A common class for users """

  EMAIL_REG = r'[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+'

  # ****************************************************************
  # Attributes & Constructor

  def __init__(
    self,
    id: Union[int, str],
    name: str,
    firstname: str,
    lastname: str,
    login: str,
    email: str = None,
    description: str = None,
  ):
    """ Constructor """

    super().__init__(id=id, name=name, label=label, desctiption=description, asset_type=AssetType.USER)
    
    self.firstname = firstname
    self.lastname = lastname
    
    self.email = self.set_email(email)      
    self.login = login

  # ****************************************************************
  # Methods
  
  def get_firstname(self) -> str:
    """ Getter for the user's firstname """
    return self.firstname
  
  def get_lastname(self) -> str:
    """ Getter for the user's lastname """
    return self.lastname
  
  def get_email(self) -> str:
    """ Getter for the user's email address """
    return self.email
  
  def get_login(self) -> str:
    """ Getter for the user's login """
    return self.login
  
  def set_email(self, email: str) -> None:
    """ Setter for the user's email address """

    if re.match(self.EMAIL_REG, email):
      self.email = email


  def to_dict(self) -> Dict:
    """ Converts the current instance into a dictionary """
    return {
      **super().to_dict(),
      "firstname": self.firstname,
      "lastname": self.lastname,
      "email": self.email,
      "login": self.login
    }