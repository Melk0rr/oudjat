from enum import Enum

class LDAPUserType(Enum):
  """ LDAP User type enum """
  
  PERSON = {}
  SERVICE = {}
  GENERIC = {}