from enum import Enum

class ADAttributes(Enum):
  """ AD Attributes by object type """
  user = [
    "accountExpires",
    "cn",
    "description",
    "employeeID",
    "givenName",
    "lastLogon",
    "mail",
    "objectSid",
    "pwdLastSet",
    "sn",
    "sAMAccountName",
    "title",
    "userAccountControl",
    "whenChanged",
    "whenCreated"
  ]

  computer = [
    "description"
    "objectSid",
    "whenChanged",
    "whenCreated"
  ]