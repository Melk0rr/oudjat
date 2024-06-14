import json
import pkgutil
from typing import List, Dict
from ldap3 import Server, Connection, ALL, SUBTREE, NTLM

from oudjat.utils.file import import_json
from oudjat.connectors.ad.ad_attributes import get_ad_attributes

class ADConnector:
  """ AD helper with functions to query domain using LDAP filters """
  ldap_flags = {
    "ACCOUNT_DISABLE": 2,
    "HOMEDIR_REQUIRED": 8,
    "LOCKOUT": 16,
    "PASSWD_NOTREQD": 32,
    "PASSWD_CANT_CHANGE": 64,
    "ENCRYPTED_TEXT_PASSWORD_ALLOWED": 128,
    "NORMAL_ACCOUNT": 512,
    "INTERDOMAIN_TRUST_ACCOUNT": 2048,
    "WORKSTATION_TRUST_ACCOUNT": 4096,
    "SERVER_TRUST_ACCOUNT": 8192,
    "DONT_EXPIRE_PASSWD": 65536,
    "MNS_LOGON_ACCOUNT": 131072,
    "SMARTCARD_REQUIRED": 262144,
    "TRUSTED_FOR_DELEGATION": 524288,
    "NOT_DELEGATED": 1048576,
    "USE_DES_KEY_ONLY": 2097152,
    "DONT_REQUIRE_PREAUTH": 4194304,
    "PASSWORD_EXPIRED": 8388608,
    "TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION": 16777216,
    "NO_AUTH_DATA_REQUIRED": 33554432,
    "PARTIAL_SECRETS_ACCOUNT": 67108864
  }
  
  object_filters = {
    "user": "(&(objectClass=user)(!(objectClass=computer)))",
    "computer": "(&(objectClass=computer)(!(objectClass=user)))"
  }

  def __init__(self, server: str, ad_user: str, ad_password: str, use_tls: bool = False):
    """ Constructor """
    server_split = server.split('.')
    domain_components = server_split[1:]

    self.server_hostname = server_split[0]
    self.domain = '.'.join(domain_components)
    self.default_search_base = ','.join([ f"DC={component}" for component in domain_components ])

    port = 636 if use_tls else 389
    self.server = Server(server, get_info=ALL, port=port, use_ssl=use_tls, allowed_referral_hosts=[('*', True)])
    self.connection = Connection(self.server, user=ad_user, password=ad_password, auto_bind=True, auto_referrals=False, authentication=NTLM)

  def get_properties(self):
    """ Getter for AD properties """
    return self.properties

  def get_domain(self):
    """ Getter for AD domain """
    return self.domain

  def get_default_search_base(self):
    """ Getter for the default search base """
    return self.default_search_base

  def base_search(self, attributes: List[str] = [], search_filter: str = None, search_type: str = "user", search_base: str = None):
    """ Base search function """
    if self.connection is None:
      raise ValueError(f"Error while searching {self.server_hostname}: connection was not setup")
    
    # If a filter is provided : combine with the object filter
    final_filter = self.object_filters[search_type]
    if search_filter:
      final_filter = f"(&{final_filter}{search_filter})"

    # Default search base is domain root
    if search_base is None:
      search_base = self.default_search_base

    if len(attributes) == 0:
      attributes = get_ad_attributes(search_type)

    raw_search = self.connection.extend.standard.paged_search(
      search_base=search_base,
      search_filter=final_filter,
      attributes=attributes,
      search_scope=SUBTREE,
      generator=False
    )
    
    return raw_search
  
  def clean_results(self, search_result: List[Dict]):
    """ Filter results to keep only searchResEntry and remove useless attributes """
    return [ { "dn": e.get("dn", ""), **e.get("attributes", {}) } for e in search_result if e["type"] == "searchResEntry" ]

  def get_ad_users(self, search_filter: str = None, search_base: str = None, attributes: List[str] = []):
    """ Retreive user objects from the domain """

    user_search = self.base_search(search_filter=search_filter, attributes=attributes, search_base=search_base, search_type="user")
    users = self.clean_results(user_search)

    return users

  def get_ad_computers(self, search_filter: str = None, search_base: str = None, attributes: List[str] = []):
    """ Retreive computer objects from the domain """
      
    computer_search = self.base_search(search_filter=search_filter, attributes=attributes, search_base=search_base, search_type="computer")
    computers = self.clean_results(computer_search)
    
    return computers
