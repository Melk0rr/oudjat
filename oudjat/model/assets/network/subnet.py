from typing import List, Union

from oudjat.utils import i_or, i_and
from . import IPv4, IPv4Mask, ip_int_to_str

class Subnet:
  """ A class to handle subnets """
  
  # ****************************************************************
  # Attributes & Constructors
  
  def __init__(
    self,
    addr: Union[str, IPv4],
    name: str,
    mask: Union[int, str, IPv4Mask],
    description: str = None,
    hosts: Union[List[IPv4], List[str]] = None
  ):
    """ Constructor """
    
    if not isinstance(addr, IPv4):
      addr = IPv4(addr)

    if mask is None:
      raise ValueError(f"Subnet::Provided net address has no mask set: {addr.get_address()}")
     
    self.mask: IPv4Mask = None

    # Try to extract mask if provided as CIDR notation
    cidr = None
    if (type(address) is str) and ("/" in address):
      address, cidr = address.split("/")
      cidr = int(cidr)
      
    self.address: IPv4 = addr.get_net_addr()
    self.mask: IPv4Mask = self.set_mask(mask)
    self.broadcast = self.get_broadcast_address()

    self.name = name
    self.description = description
    
    self.hosts = {}

    if hosts is not None:
      for ip in hosts:
        self.add_host(ip)

        
  # ****************************************************************
  # Methods
  
  def get_name(self) -> str:
    """ Getter for the subnet name """
    return self.name
  
  def get_description(self) -> str:
    """ Getter for the subnet description """
    return self.description

  def get_address(self) -> IPv4:
    """ Getter for subnet address """
    return self.address
  
  def get_mask(self) -> IPv4Mask:
    """ Getter for ip mask instance """
    return self.mask
  
  def get_broadcast_address(self) -> IPv4:
    """ Returns the broadcast address of the current subnet """
    broadcast_int = i_or(int(self.address.get_mask().get_wildcard()), int(self.address))
    return IPv4(ip_int_to_str(broadcast_int) + f"/{self.mask.get_cidr()}")

  def set_mask(self, mask: Union[int, str, IPv4Mask]):
    """ Setter for ip mask """
    if not isinstance(mask, IPv4Mask):
      mask = IPv4Mask(mask)

    self.mask = mask

  def contains(self, ip: Union[str, IPv4]) -> bool:
    """ Checks wheither the provided IP is in the current subnet """
    if not isinstance(ip, IPv4):
      ip = IPv4(ip)

    mask_address = int(self.mask)
    return i_and(int(ip), mask_address) == i_and(int(self.address), mask_address)

  def list_addresses(self) -> List[str]:
    """ Lists all possible hosts in subnet """
    start = self.address.get_address() + 1
    end = self.broadcast.get_address()

    return [ f"{ip_int_to_str(i)}/{self.mask.get_cidr()}" for i in range(start, end) ]

  def add_host(self, host: Union[str, IPv4]) -> None:
    """ Adds a new host to the subnet """
    
    if not isinstance(host, IPv4):
      host = IPv4(host)
      
    if (self.contains(host) and (int(host) != int(self.address)) and (int(host) != int(self.broadcast))):
      self.hosts[str(host)] = host

  def __str__(self, showDescription: bool = False) -> str:
    """ Returns a string based on current instance """
    sub_str = f"{self.name}: {self.address}/{self.mask.get_cidr()}"

    if showDescription:
      sub_str += f" ({self.description})"

    return sub_str
