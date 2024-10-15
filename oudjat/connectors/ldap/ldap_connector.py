import ssl
import ldap3
import socket

from typing import List, Union, Any

from oudjat.utils import ColorPrint

from oudjat.connectors import Connector
from oudjat.connectors.ldap.objects import LDAPEntry, LDAPObjectType, LDAPGroupPolicyObject
from oudjat.connectors.ldap.objects.subnet import LDAPSubnet

class LDAPConnector(Connector):
  """ LDAP connector to interact and query LDAP servers """

  # ****************************************************************
  # Attributes & Constructors
  def __init__(
    self,
    server: str,
    service_name: str = "OudjatLDAPConnection",
    use_tls: bool = False
  ):
    """ Constructor """
    self.use_tls = use_tls
    self.port = 389
    if use_tls:
      self.port = 636

    super().__init__(target=server, service_name=service_name, use_credentials=True)

    self.default_search_base: str = None
    self.ldap_server: ldap3.Server = None
    self.connection: ldap3.Connection = None
    self.domain: str = None

  # ****************************************************************
  # Methods

  def get_domain(self) -> str:
    """ Getter for AD domain """
    return self.domain

  def get_connection(self):
    """ Getter for the server connection """
    return self.connection

  def get_default_search_base(self) -> str:
    """ Getter for the default search base """
    return self.default_search_base

  def set_tls_usage(self, use_tls: bool = True) -> None:
    """ Setter for connector tls usage """
    self.use_tls = use_tls
    if use_tls:
      self.port = 636
    
    else:
      self.port = 389
    
  def connect(self, version: ssl._SSLMethod = None) -> None:
    """ Initiate connection to target server """

    if version is None:
      try:
        self.connect(version=ssl.PROTOCOL_TLSv1_2)
        
      except ldap3.core.exceptions.LDAPSocketOpenError as e:
        if not self.use_tls:
          ColorPrint.yellow(f"Got error while trying to connect to LDAP: {e}")

        self.connect(version=ssl.PROTOCOL_TLSv1)

      return

    target_ip = socket.gethostbyname(self.target)
    
    if not target_ip:
      raise Exception(f"The target {self.target} is unreachable")

    tls_option = { "use_ssl": self.use_tls }
    if self.use_tls:
      tls_option["tls"] = ldap3.Tls(validate=ssl.CERT_NONE, version=version, ciphers='ALL:@SECLEVEL=0')

    ldap_server = ldap3.Server(
      target_ip,
      get_info=ldap3.ALL,
      port=self.port,
      **tls_option
    )

    ldap_connection = ldap3.Connection(
      ldap_server,
      user=self.credentials.username,
      password=self.credentials.password,
      auto_referrals=False,
      authentication=ldap3.NTLM
    )

    if not ldap_connection.bound:
      
      bind_result = ldap_connection.bind()

      if not bind_result:
        result = ldap_connection.result

        if result["result"] == "RESULT_STRONGER_AUTH_REQUIRED" and self.use_tls:
          self.set_tls_usage(use_tls=True)
          return self.connect()
        
        else:
          if result["description"] == "invalidCredentials" and result["message"].split(":")[0] == "80090346":
            raise Exception(
              "Failed to bind to LDAP. LDAP channel binding or signing is required. Use -scheme ldaps -ldap-channel-binding"
            )

          raise Exception(
            f"Failed to authenticate to LDAP: ({result['description']}) {result['message']}]")

    if ldap_server.schema is None:
      ldap_server.get_info_from_server(ldap_connection)

      if ldap_connection.result["result"] != 0:
        if ldap_connection.result["message"].split(":")[0] == "000004DC":
          raise Exception(
            "Failed to bind to LDAP. This is most likely because of an invalid username specified for logon"
          )

      if ldap_server.schema is None:
        raise Exception("Failed to get LDAP schema")

    ColorPrint.green(f"Bound to {ldap_server}")

    self.ldap_server = ldap_server
    self.connection = ldap_connection

    self.default_search_base = self.ldap_server.info.other["defaultNamingContext"][0]
    self.domain = self.ldap_server.info.other["ldapServiceName"][0].split("@")[-1]

  def search(
    self,
    search_type: str = "DEFAULT",
    search_base: str = None,
    search_filter: str = None,
    attributes: Union[str, List[str]] = None,
    **kwargs
  ) -> List[LDAPEntry]:
    """ Runs an LDAP search based on the provided parameters """
    
    if self.connection is None:
      raise ConnectionError(f"You must initiate connection to {self.target} before running search !")

    search_type = search_type.upper()
    if search_type not in LDAPObjectType.__members__:
      raise ValueError(f"Invalid search type proviced: {search_type}")

    if search_base is None:
      search_base = self.default_search_base 

    formated_filter = LDAPObjectType[search_type].value.get("filter", "")
    if search_type.lower() == "default" and search_filter is not None:
      formated_filter = search_filter

    else:
      if search_filter:
        formated_filter = f"(&{formated_filter}{search_filter})"

    # print(formated_filter)

    if attributes is None:
      attributes = LDAPObjectType[search_type].value.get("attributes", "*")

    results = self.connection.extend.standard.paged_search(
      search_base=search_base,
      search_filter=formated_filter,
      attributes=attributes,
      generator=False,
      **kwargs
    )

    entries = list(
      map(
        lambda entry: LDAPEntry(**entry),
        filter(
          lambda entry: entry["type"] == "searchResEntry",
          results
        )
      )
    )

    return entries

  def get_gpo(
    self,
    displayName: str = "*",
    name: str = "*",
    attributes: Union[str, List[str]] = None
  ) -> List[LDAPGroupPolicyObject]:
    """ Specific GPO retreiving method """
    gpo_entries = self.search(
      search_type="GPO",
      search_base=None,
      search_filter=f"(displayName={displayName})(name={name})",
      attributes=attributes
    )

    gpos = list(
      map(
        lambda entry: LDAPGroupPolicyObject(ldap_entry=entry),
        gpo_entries
      )
    )
    
    return gpos

  def get_subnet(
    self,
    search_filter: str = None,
    attributes: Union[str, List[str]] = None
  ) -> List:

    sb_dc = ','.join([ f"DC={dc.lower()}" for dc in self.domain.split('.') ])
    
    subnet_entries = self.search(
      search_type="SUBNET",
      search_base=f"CN=Subnets,CN=Sites,CN=Configuration,{sb_dc}",
      search_filter=search_filter,
      attributes=attributes
    )

    subnet = list(
      map(
        lambda entry: LDAPSubnet(ldap_entry=entry),
        subnet_entries
      )
    )
    
    return subnet