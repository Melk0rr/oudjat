from typing import List
from . import IPv4

class Subnet:
  """ A class to handle subnets """
  
  # ****************************************************************
  # Attributes & Constructors
  
  def __init__(self, addr: IPv4, name: str, description: str, hosts: List[IPv4]):
    """ Constructor """
    self.addr = addr
    self.name = name
    self.description = description
    
    self.hosts = {}