import winrm

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

  def connect(self) -> None:
    """ Connects to server with WMI """
    try:
      self.connection = winrm.Session(
        self.target,
        transport=self.scheme,
        username=self.credentials.username,
        password=self.credentials.password
      )

      self.wmi = winrm.WMI(self.connection)
      
    except Exception as e:
      raise(f"An error occured while connecting to {self.target} with WMI\n{e}")
    
  def search(self) -> None:
    """ Runs a search query based on provided parameters """
    
  def get_gpo_wmi_filters(self, gpo_dn: str) -> List:
    """ Retreives the names of WMI filters of a given gpo """
    
    try:
      gpo_obj = self.wmi["GPMC_GPO"].Win32Path(gpo_dn)
      
      if not gpo_obj.IsDeleted():
        print(gpo_obj)
        filters = []
        
        for filter_prop in ['WMIFilterName', 'ADMXInstallDN']:
          value = getattr(gpo_obj, filter_prop)
          
          if value is not None and len(value) > 0:
            filters.extend([filter_.strip() for filter_ in value.split(';')])
        
        return list(set(filters))
    
    except Exception as e:
      print(f"Error retrieving WMI filters for GPO '{gpo_dn}': {e}")
      return []