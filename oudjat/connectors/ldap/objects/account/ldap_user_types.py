from typing import List, Dict

from oudjat.control.data import DataFilter

PERSON_REG = r"^[a-zA-ZàáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð '-]+$"

class LDAPUserType:
  """ LDAP User types """
  
  # ****************************************************************
    # Attributes & Constructors

  def __init__(
    self,
    name: str,
    filters: Union[List[Dict], List[DataFilter]],
    description: str = None
  ):
    """ Constructor """

    self.name = name
    self.description = description
    
    self.filters = []
    if not isinstance(filters, list):
      filters = [ filters ]
      
    self.filters = DataFilter.gen_from_dict(filters)

  # ****************************************************************
  # Methods
  
  def get_name() -> str:
    """ Getter for ldap user type name """
    return self.name
  
tree = {
  "node": {
    "operator": "or",
    "leaves": [
      {
        "fieldname": "employeeID",
        "operator": "isnt",
        "value": None
      }
    ],
    "node": {
      "operator": "and",
      "leaves": [
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
  }
}


LDAPUserType = {
  PERSON: {
    "join_operator": "or",
    "filters": [
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
      {
        "fieldname": "employeeID",
        "operator": "isnt",
        "value": None
      }
    ]
  },

  SERVICE: [
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
  ],

  GENERIC: []
}
