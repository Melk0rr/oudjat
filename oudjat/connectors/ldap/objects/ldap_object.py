from typing import List, Dict

from oudjat.utils import date_format_from_flag, DATE_TIME_FLAGS
from oudjat.connectors.ldap.objects import LDAPEntry

def parse_dn(dn: str) -> Dict:
  """ Parses a DN into pieces """
  split = dn.split(',')
  pieces = {}
  
  for p in split:
    p_split = p.split('=')
    
    if p_split[0] not in pieces.keys():
      pieces[p_split[0]] = []
      
    pieces[p_split[0]].append(p_split[1])
    
  return pieces

class LDAPObject:
  """ Generic LDAP object """

  # ****************************************************************
  # Attributes & Constructors
  def __init__(self, ldap_entry: LDAPEntry):
    """ Constructor """
    
    self.entry = ldap_entry
    self.dn = self.entry.get_dn()
    self.name = self.entry.get("name")
    self.guid = self.entry.get("objectGUID")
    self.sid = self.entry.get("objectSid")
    self.description = ' '.join(self.entry.get("description", []))

    self.object_classes = self.entry.get("objectClass", [])
    
    self.dn_pieces = parse_dn(self.dn)
    self.domain = '.'.join(self.dn_pieces.get("DC")).lower()

    self.creation_date = self.entry.get("whenCreated")
    self.change_date = self.entry.get("whenChanged")
    
    self.followup_flags: List[str] = []

  # ****************************************************************
  # Methods

  def get_dn(self) -> str:
    """ Getter for ldap object dn """
    return self.dn
  
  def get_name(self) -> str:
    """ Getter for ldap object name """
    return self.name
  
  def get_sid(self) -> str:
    """ Getter for ldap object sid """
    return self.sid

  def get_entry(self) -> Dict:
    """ Getter for entry attributes """
    return self.entry
  
  def get_dn_pieces(self) -> Dict:
    """ Getter for object dn pieces """
    return self.dn_pieces
  
  def get_description(self) -> str:
    """ Getter for ldap object description """
    return self.description

  def get_domain(self) -> str:
    """ Getter for object domain """
    return self.domain
  
  def get_creation_date(self) -> str:
    """ Getter for ldap object creation date"""
    return self.creation_date

  def get_change_date(self) -> str:
    """ Getter for ldap object change date"""
    return self.change_date

  def is_of_object_class(self, obj_cl: str) -> bool:
    """ Checks if the current object is of given class """
    return obj_cl.lower() in self.object_classes

  def to_dict(self) -> Dict:
    """ Converts the current instance into a dict """
    return {
      "dn": self.dn,
      "name": self.name,
      "guid": self.guid,
      "sid": self.sid,
      "description": self.description,
      "domain": self.domain,
      "creation_date": self.creation_date.strftime(date_format_from_flag(DATE_TIME_FLAGS)),
      "change_date": self.change_date.strftime(date_format_from_flag(DATE_TIME_FLAGS))
    }