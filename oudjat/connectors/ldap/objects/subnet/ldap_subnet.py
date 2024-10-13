from typing import List

from oudjat.model.network import Subnet
from oudjat.connectors.ldap.objects import LDAPObject

class LDAPSubnet(Subnet, LDAPObject):
  """ A class to describe LDAP subnet objects """

  # ****************************************************************
  # Attributes & Constructors

  # ****************************************************************
  # Methods