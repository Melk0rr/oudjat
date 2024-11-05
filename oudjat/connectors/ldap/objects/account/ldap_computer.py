
from oudjat.model.assets.computer import Computer
from oudjat.model.assets.software.os import OperatingSystem, OSOption
from oudjat.connectors.ldap.objects import LDAPEntry

from . import LDAPAccount

class LDAPComputer(LDAPAccount, Computer):
  """ A class to describe LDAP computer objects """
  
  # ****************************************************************
    # Attributes & Constructors

  def __init__(self, ldap_entry: LDAPEntry):
    """ Construcotr """

    super().__init__(ldap_entry=ldap_entry)

    os_family_infos = OperatingSystem.get_matching_os_family(self.entry.get("operatingSystem"))
    
    os = None
    
    if os_family_infos is not None:
      os = OSOption[os_family_infos.replace(' ', '').upper()].value

      if len(os.get_releases()) == 0:
        os.gen_releases()      
      
    
    print(os)

  # ****************************************************************
  # Methods