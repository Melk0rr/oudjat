
from oudjat.connectors import Connector

class WMIConnector(Connector):
  """ A class to use WMI """

  # ****************************************************************
  # Attributes & Constructors
  def __init__(
    self,
    server: str,
    service_name: str = "OudjatLDAPConnection"
  ):
    """ Constructor """
    super().__init__(target=server, service_name=service_name, use_credentials=True)

    self.connection = None
    self.wmi = None
    self.scheme = "https"
