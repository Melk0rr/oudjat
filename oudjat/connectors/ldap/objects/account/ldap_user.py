from typing import Dict

from oudjat.model.assets.user import User
from oudjat.connectors.ldap.objects import LDAPEntry

from . import LDAPAccount

class LDAPUser(LDAPAccount, User):
  """ A class to describe LDAP user objects """

  # ****************************************************************
    # Attributes & Constructors

  def __init__(self, ldap_entry: LDAPEntry):
    """ Constructor """

    super().__init__(ldap_entry=ldap_entry)

    self.employeeId = self.entry.get("employeeID", None)
    self.manager = self.entry.get("manager", None)

    User.__init__(
      self,
      id=self.uuid,
      name=self.name,
      firstname=self.entry.get("givenName"),
      lastname=self.entry.get("surName"),
      email=self.entry.get("mail", None),
      login=self.san,
      description=self.description,
    )

  # ****************************************************************
  # Methods
  
  def get_employee_id(self) -> str:
    """ Getter for the employee id """
    return self.employeeId
  
  def get_manager(self) -> str:
    """ Getter for the user's manager """
    return self.manager
  
  def to_dict(self) -> Dict:
    """ Converts the current instance into a dictionary """
    base_dict = super().to_dict()
    base_dict.pop("san")

    user_dict = User.to_dict(self)

    return {
      **base_dict,
      "employeeID": self.employeeId,
      "manager": self.manager,
      **user_dict
    }