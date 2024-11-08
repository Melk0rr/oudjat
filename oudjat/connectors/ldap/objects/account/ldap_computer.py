
from oudjat.model.assets.computer import Computer
from oudjat.model.assets.software import SoftwareEdition
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

    raw_os = self.entry.get("operatingSystem")
    os_family_infos: str = OperatingSystem.get_matching_os_family(raw_os)
    os, os_edition = None
    
    if os_family_infos is not None:
      os: OperatingSystem = OSOption[os_family_infos.replace(' ', '').upper()].value

      if os is not None:
        if len(os.get_releases()) == 0:
          os.gen_releases()      
      
        os_edition: List[SoftwareEdition] = os.get_matching_editions(raw_os)
        
    if os_edition is not None and len(os_edition) != 0:
      os_edition = os_edition[0]
    
    Computer.__init__(
      self,
      id=self.uuid,
      name=self.name,
      os=os,
      os_edition=os_edition
    )

    print(self.is_os_supported())

  # ****************************************************************
  # Methods