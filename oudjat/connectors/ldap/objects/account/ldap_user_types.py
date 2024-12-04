from typing import List, Dict

PERSON_REG = r"^[a-zA-ZàáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð '-]+$"

LDAPUserType = {
  "PERSON": {
    "description": "User account binded to a physical person",
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

  "SERVICE": {
    "description": "User account used to run a service or for application purposes",
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
  },

  "GENERIC": {
    "description": "User account used by multiple persons"
  }
}