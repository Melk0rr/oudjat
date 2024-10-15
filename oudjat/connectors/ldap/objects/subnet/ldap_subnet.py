from typing import List

from oudjat.model.network import Subnet
from oudjat.connectors.ldap.objects import LDAPObject, LDAPEntry

class LDAPSubnet(LDAPObject, Subnet):
  """ A class to describe LDAP subnet objects """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, ldap_entry: LDAPEntry):
    """ Constructor """
    super(LDAPObject, self).__init__(ldap_entry=ldap_entry)
    super(Subnet, self).__init__(addr=ldap_entry.get("name"))

  # ****************************************************************
  # Methods