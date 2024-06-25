import ssl
import json
import ldap3
import socket

from typing import List, Union, Any

from oudjat.utils.color_print import ColorPrint
from oudjat.connectors.ldap.ldap_search_types import LDAPSearchTypes

class LDAPEntry(dict):
  """ LDAP entry dict """

  def get(self, key: str) -> Any:
    """ Retreive the value of the given attribute """
    if key not in self.__getitem__("attributes").keys():
      return None

    item = self.__getitem__("attributes").__getitem__(key)

    if isinstance(item, list) and len(item) == 0:
      return None

    return item

  def set(self, key: str, value: Any) -> Any:
    """ Set the given value of the provided attribute """
    return self.__getitem__("attributes").__setitem__(key, value)

  def get_raw(self, key: str) -> Any:
    """ Retreive the value of the given raw attribute """
    if key not in self.__getitem__("raw_attributes").keys():
      return None

    return self.__getitem__("raw_attributes").__getitem__(key)

  def attr(self):
    """ Retreive ldap attributes """
    return self.__getitem__("attributes")

class LDAPConnector:
  """ LDAP connector to interact and query LDAP servers """

  def __init__(
    self,
    server: str,
    ldap_user: str,
    ldap_password: str,
    use_tls: bool = False
  ):
    """ Constructor """
    self.target = server
    self.use_tls = use_tls
    self.port = 389
    if use_tls:
      self.port = 636

    self.ldap_credentials = { "user": ldap_user, "password": ldap_password }

    self.default_search_base: str = None
    self.ldap_server: Server = None
    self.ldap_connection: ldap3.Connection = None
    self.domain: str = None

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
      user=self.ldap_credentials["user"],
      password=self.ldap_credentials["password"],
      auto_referrals=False,
      authentication=ldap3.NTLM
    )

    if not ldap_connection.bound:
      
      bind_result = ldap_connection.bind()

      if not bind_result:
        result = ldap_connection.result

        if result["result"] == RESULT_STRONGER_AUTH_REQUIRED and self.use_tls:
          logging.warning(
              "LDAP Authentication is refused because LDAP signing is enabled. "
              "Trying to connect over LDAPS instead..."
          )

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
    self.ldap_connection = ldap_connection

    self.default_search_base = self.ldap_server.info.other["defaultNamingContext"][0]
    self.domain = self.ldap_server.info.other["ldapServiceName"][0].split("@")[-1]

  def search(
    self,
    search_type: str = "USER",
    search_base: str = None,
    search_filter: str = None,
    attributes: Union[str, List[str]] = None,
    **kwargs
  ) -> List["LDAPEntry"]:
    """ Runs an Active directory search based on the provided parameters """
    
    if self.ldap_connection is None:
      raise ConnectionError(f"You must initiate connection to {self.target} before running search !")

    if search_base is None:
      search_base = self.default_search_base 

    search_type = search_type.upper()

    formated_filter = LDAPSearchTypes[search_type].value["filter"]
    if search_filter:
      formated_filter = f"(&{formated_filter}{search_filter})"

    if attributes is None:
      attributes = LDAPSearchTypes[search_type].value["attributes"]

    results = self.ldap_connection.extend.standard.paged_search(
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