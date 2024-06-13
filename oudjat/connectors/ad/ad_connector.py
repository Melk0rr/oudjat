import json
import pkgutil
from typing import List, Dict
from ldap3 import Server, Connection, ALL, SUBTREE, NTLM

from oudjat.utils.file import import_json

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

  attributes = import_json("oudjat/connectors/ad/config/attributes.json")

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

  def base_search(self, search_filter: str, attributes: List[str], search_base: str = None):
    """ Base search function """
    if self.connection is None:
      raise ValueError(f"Error while searching {self.server_hostname}: connection was not setup")

    if search_base is None:
      search_base = self.default_search_base

    raw_search = self.connection.extend.standard.paged_search(
      search_base=search_base,
      search_filter=search_filter,
      attributes=attributes,
      search_scope=SUBTREE,
      generator=False
    )
    
    return raw_search

  def get_ad_users(self, search_filter: str = None, search_base: str = None, attributes: List[str] = []):
    """ Retreive users from the domain """
    user_filter = "(&(objectClass=user)(!(objectClass=computer)))"
    if search_filter:
      user_filter = f"(&{user_filter}{search_filter})"

    if len(attributes) == 0:
      attributes = self.attributes["user"]

    user_search = self.base_search(search_filter=user_filter, attributes=attributes, search_base=search_base)
    users = [ { "dn": u.get("dn", ""), **u.get("attributes", {}) } for u in user_search if u["type"] == "searchResEntry" ]

    return users
