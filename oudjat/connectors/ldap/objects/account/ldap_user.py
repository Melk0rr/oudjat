from oudjat.connectors.ldap.objects import LDAPEntry
from . import LDAPAccount

class LDAPUser(LDAPAccount):
  """ A class to describe LDAP user objects """

  # ****************************************************************
    # Attributes & Constructors

  def __init__(self, ldap_entry: LDAPEntry):
    """ Construcotr """

    # TODO: user locked
    # TODO: user must change pwd at next logon

  # ****************************************************************
  # Methods
  