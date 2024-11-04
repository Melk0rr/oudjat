
from oudjat.model.assets.computer import Computer
from oudjat.model.assets.software.os import get_matching_os_family
from oudjat.connectors.ldap.objects import LDAPEntry

from . import LDAPAccount

class LDAPComputer(LDAPAccount, Computer):
  """ A class to describe LDAP computer objects """
  
  # ****************************************************************
    # Attributes & Constructors

  def __init__(self, ldap_entry: LDAPEntry):
    """ Construcotr """

    super().__init__(ldap_entry=ldap_entry)

    os_family = get_matching_os_family(self.entry.get("operatingSystem"))
    print(os_family)

  # ****************************************************************
  # Methods