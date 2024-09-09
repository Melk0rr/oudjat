from typing import List

import oudjat.connectors.ldap.objects as ldapobj

from oudjat.connectors.ldap.objects import LDAPEntry

class LDAPMapper:
  # ****************************************************************
  # Static methods
  @staticmethod
  def map(entries: List[LDAPEntry], obj_type: str) -> List:
    """ Maps LDAP entries into ldap object type """
    ldap_objects = {
      "GPO": ldapobj.LDAPGroupPolicyObject
    }

    mapped = map(
      lambda entry: ldap_objects[obj_type](ldap_entry=entry),
      gpo_entries
    )

    return mapped