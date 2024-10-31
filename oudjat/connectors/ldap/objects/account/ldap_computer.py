from oudjat.model.assets.computer import Computer
from oudjat.connectors.ldap.objects import LDAPEntry
from . import LDAPAccount

class LDAPComputer(LDAPAccount, Computer):
  """ A class to describe LDAP computer objects """
  
  # ****************************************************************
    # Attributes & Constructors

  def __init__(self, ldap_entry: LDAPEntry):
    """ Construcotr """

  # ****************************************************************
  # Methods