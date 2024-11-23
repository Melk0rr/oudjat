from enum import Enum


PERSON_REG = r"^[a-zA-ZàáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð '-]+$"

class LDAPUserType(Enum):
  """ LDAP User type enum """
  
  PERSON = {
    "filters": [
      {
        "fieldname": "sn",
        "operation": "match",
        "value": PERSON_REG
      },
      {
        "fieldname": "givenName",
        "operation": "match",
        "value": PERSON_REG
      },
      {
        "fieldname": "employeeID",
        "operator": "isnt",
        "value": None
      }
    ]
  }
  SERVICE = {
    "filters": [
      {
        "fieldname": "sAMAccountName",
        "operator": "match",
        "value": r'^svc[-_].*$'
      },
      {
        "fieldname": "distinguishedName",
        "operator": "search",
        "value": r'OU=Service Accounts|OU=Services,OU=Users,DC='
      }
    ]
  }
  GENERIC = {}