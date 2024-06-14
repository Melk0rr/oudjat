import json
import pkgutil
from typing import List, Dict
from ldap3 import Server, Connection, ALL, NTLM

from oudjat.connectors.ad.ad_attributes import ADAttributes
from oudjat.connectors.ad.ad_filters import ADSearchFilters
from oudjat.connectors.ad.ad_search import ADSearch

class ADConnector:
  """ AD helper with functions to query domain using LDAP filters """

  def __init__(
    self,
    server: str,
    ad_user: str,
    ad_password: str,
    use_tls: bool = False
  ):
    """ Constructor """
    server_split = server.split('.')
    domain_components = server_split[1:]

    self.server_hostname = server_split[0]
    self.domain = '.'.join(domain_components)
    self.default_search_base = ','.join([ f"DC={component}" for component in domain_components ])

    port = 636 if use_tls else 389
    self.server = Server(server, get_info=ALL, port=port, use_ssl=use_tls, allowed_referral_hosts=[('*', True)])
    self.connection = Connection(self.server, user=ad_user, password=ad_password, auto_bind=True, auto_referrals=False, authentication=NTLM)

  def get_domain(self):
    """ Getter for AD domain """
    return self.domain

  def get_connection(self):
    """ Getter for the server connection """
    return self.connection

  def get_default_search_base(self):
    """ Getter for the default search base """
    return self.default_search_base

  def search(
    self,
    search_type: str = "user",
    search_base: str = None,
    search_filter: str = None,
    attributes: List[str] = []
  ):
    """ Runs an Active directory search based on the provided parameters """

    formated_filter = ADSearchFilters[search_type].value
    if search_filter:
      formated_filter = f"(&{formated_filter}{search_filter})"

    if len(attributes) == 0:
      attributes = ADAttributes[search_type].value

    search = ADSearch(connector=self, search_base=search_base, search_filter=formated_filter, attributes=attributes)
    return search.run()

  def get_ad_users(
    self,
    search_base: str = None,
    search_filter: str = None,
    attributes: List[str] = []
  ):
    """ Retreive users from current domain """
    return self.search("user", search_base, search_filter, attributes)
  
  def get_ad_computers(
    self,
    search_base: str = None,
    search_filter: str = None,
    attributes: List[str] = []
  ):
    """ Retreive computers from current domain """
    return self.search("computer", search_base, search_filter, attributes)