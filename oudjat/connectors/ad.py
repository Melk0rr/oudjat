from typing import List, Dict
from ldap3 import Server, Connection, ALL, SUBTREE, NTLM

class AD:
  """ AD helper with functions to query domain using LDAP filters """

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

  def get_ad_users(self, search_filter: str = None, search_base: str = None):
    """ Retreive users from the domain """
    user_filter = "(&(objectClass=user)(!(objectClass=computer)))"
    if search_filter:
      user_filter = f"(&{user_filter}{search_filter})"

    print(f"Final filter: {user_filter}")

    user_attributes = ["cn", "givenName", "sn", "sAMAccountName"]

    user_search = self.base_search(search_filter=user_filter, attributes="*", search_base=search_base)
    users = [ { "dn": u.get("dn", ""), **u.get("attributes", {}) } for u in user_search if u["type"] == "searchResEntry" ]

    return users
