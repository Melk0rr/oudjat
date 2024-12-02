from typing import List, Dict

PERSON_REG = r"^[a-zA-ZàáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð '-]+$"

class LDAPUserType:
  """ A class to list LDAP user types in order to categorize users """

  PERSON = {
    "description": "",
    "tree": {
      "operator": "or",
      "nodes": [
        {
          "fieldname": "employeeID",
          "operator": "isnt",
          "value": None
        },
        {
          "operator": "and",
          "nodes": [
            {
              "fieldname": "sn",
              "operator": "match",
              "value": PERSON_REG
            },
            {
              "fieldname": "givenName",
              "operator": "match",
              "value": PERSON_REG
            },
          ]
        }
      ]
    }
  },

  SERVICE = {
    "description": "",
    "tree": {
      "operator": "or",
      "nodes": [
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
  }
  
  @staticmethod
  def options() -> List[Dict]:
    """ List options """
    