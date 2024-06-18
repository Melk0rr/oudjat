import json
import ldap3
from typing import List, Union

from oudjat.connectors.ldap.ldap_search_types import LDAPSearchTypes
from oudjat.connectors.ldap.ldap_search import LDAPSearch



class LDAPConnector:
  """ AD helper with functions to query domain using LDAP filters """

  def __init__(
    self,
    server: str,
    ad_user: str,
    ad_password: str,
    use_tls: bool = False
  ):
    """ Constructor """
    self.target = server
    self.port = 389
    if use_tls:
      self.port = 636

    self.default_search_base: str = None
    self.ldap_server: Server = None
    self.ldap_connection: ldap3.Connection = None
    self.domain: str = None

    server_split = server.split('.')
    domain_components = server_split[1:]

    self.server_hostname = server_split[0]
    self.domain = '.'.join(domain_components)
    self.default_search_base = ','.join([ f"DC={component}" for component in domain_components ])

    self.server = ldap3.Server(server, get_info=ldap3.ALL, port=port, use_ssl=use_tls, allowed_referral_hosts=[('*', True)])
    
    self.connection = ldap3.Connection(self.server, user=ad_user, password=ad_password, auto_bind=True, auto_referrals=False, authentication=ldap3.NTLM)
    
  def get_domain(self):
    """ Getter for AD domain """
    return self.domain

  def get_connection(self):
    """ Getter for the server connection """
    return self.connection

  def get_default_search_base(self):
    """ Getter for the default search base """
    return self.default_search_base

  def connect(self):
    """ Initiate connection to target server """


  def search(
    self,
    search_type: str = "user",
    search_base: str = None,
    search_filter: str = None,
    attributes: Union[str, List[str]] = []
  ):
    """ Runs an Active directory search based on the provided parameters """

    formated_filter = LDAPSearchTypes[search_type].value["filter"]
    if search_filter:
      formated_filter = f"(&{formated_filter}{search_filter})"

    if len(attributes) == 0:
      attributes = LDAPSearchTypes[search_type].value["attributes"]

    search = LDAPSearch(connector=self, search_base=search_base, search_filter=formated_filter, attributes=attributes)
    return search.run()

  def get_users(
    self,
    search_base: str = None,
    search_filter: str = None,
    attributes: List[str] = []
  ):
    """ Retreive users from current domain """
    return self.search("user", search_base, search_filter, attributes)
  
  def get_computers(
    self,
    search_base: str = None,
    search_filter: str = None,
    attributes: List[str] = []
  ):
    """ Retreive computers from current domain """
    return self.search("computer", search_base, search_filter, attributes)
  
  def get_persons(
    self,
    search_base: str = None,
    search_filter: str = None,
    attributes: List[str] = []
  ):
    """ Retreive persons from current domain """
    return self.search("person", search_base, search_filter, attributes)