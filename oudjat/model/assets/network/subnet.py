from typing import List, Union

from oudjat.utils import bytes_2_ipstr, b_or, int_2_bytes

from . import IPv4, IPv4Mask

class Subnet:
  """ A class to handle subnets """
  
  # ****************************************************************
  # Attributes & Constructors
  
  def __init__(
    self,
    addr: Union[str, IPv4],
    name: str,
    mask: Union[int, str, IPv4Mask] = None,
    description: str = None,
    hosts: Union[List[IPv4], List[str]] = None
  ):
    """ Constructor """
    
    if not isinstance(addr, IPv4):
      addr = IPv4(addr)

    if addr.get_mask() is None:
      if mask is None:
        raise ValueError(f"Subnet::Provided net address has no mask set: {addr.get_address()}")

      addr.set_mask(mask)

    self.addr = addr.get_net_addr()

    broadcast_bytes = [
      b_or(self.addr.bytes[i], self.addr.mask.get_wildcard().bytes[i])
      for i, x in enumerate(self.addr.bytes)
    ]
    self.broadcast = IPv4(bytes_2_ipstr(broadcast_bytes) + f"/{self.addr.mask.cidr}")

    self.name = name
    self.description = description
    
    self.hosts = {}

    if hosts is not None:
      for ip in hosts:
        if not isinstance(ip, IPv4):
          ip = IPv4(ip)
        
        if (
          (ip.is_in_subnet(self.addr.get_address())) and
          (ip.get_address() != self.addr.get_address()) and
          (ip.get_address() != self.broadcast.get_address())
        ):
          self.hosts[ip.address] = ip
        
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
    return self.addr

  def list_addresses(self) -> List[str]:
    """ Lists all possible hosts in subnet """
    start = self.addr.to_int() + 1
    end = self.broadcast.to_int()

    addresses = []
    for i in range(start, end):
      addresses.append(f"{('.'.join(f"{o}" for o in int_2_bytes(i)))}/{self.addr.get_mask().get_cidr()}")
      
    return addresses

  def add_host(self, host: Union[str, IPv4]) -> None:
    """ Adds a new host to the subnet """
    
    if not isinstance(host, IPv4):
      host = IPv4(host)
      
    if (
      (host.is_in_subnet(self.addr.get_address())) and
      (host.get_address() != self.addr.get_address()) and
      (host.get_address() != self.broadcast.get_address())
    ):
      self.hosts[host.get_address()] = host

  def to_string(self, showDescription: bool = False) -> str:
    """ Returns a string based on current instance """
    sub_str = f"{self.name}: {self.addr.get_address()}/{self.addr.get_mask().get_cidr()}"

    if showDescription:
      sub_str += f" ({self.description})"

    return sub_str