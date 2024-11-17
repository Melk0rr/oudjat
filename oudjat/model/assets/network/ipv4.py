import re

from enum import Enum
from typing import List, Union

from oudjat.utils import count_1_bits

from . import Port

def ip_str_to_int(ip: str) -> int:
  """ Converts an ip address string into an int """
  return int(''.join([bin(int(x)+256)[3:] for x in ip.split('.')]), 2)

def ip_int_to_str(ip: int) -> str:
  """ Converts an ip address integer into a string """
  return '.'.join([str((ip >> i) & 0xff) for i in (24, 16, 8, 0)])

class IPVersion(Enum):
  IPV4 = {
    "pattern": r'^(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$'
  }
  IPV6 = {
    "pattern": r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$'
  }

class IPBase:

  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, addr: str):
    """ Constructor """

    if re.match(IPVersion.IPV4.value["pattern"], addr):
      self.version = IPVersion.IPV4
    
    elif re.match(IPVersion.IPV6.value["pattern"], addr):
      self.version = IPVersion.IPV6
    
    else:
      raise ValueError(f"Invalid IPv4 address provided: {addr}")

    self.address: int = ip_str_to_int(addr)

  # ****************************************************************
  # Methods

  def get_address(self) -> str:
    """ Getter for ip string address """
    return self.address

  def __str__(self) -> str:
    """ Converts the current ip base into a string """
    return ip_int_to_str(self.address)


class IPv4Mask(IPBase):
  """ Simple Class providing tools to manipulate IPv4 mask """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, mask: Union[int, str]):
    """ Constructor """
    
    if type(mask) is str:
      super().__init__(mask)
      cidr = count_1_bits(self.address)
      
    elif type(mask) is int:
      if not 1 < mask < 33:
        raise ValueError("Mask CIDR value must be between 1 and 32!")

      cidr = mask
      super().__init__(self.get_netmask(cidr))
      
    else:
      raise ValueError(f"Invalid mask provided : {mask}. You must provide a string or an integer !")

    self.cidr = cidr

  # ****************************************************************
  # Methods

  def get_cidr(self) -> int:
    """ Getter for mask CIDR """
    return self.cidr

  def cidr_to_int(self) -> int:
    """ Returns the current mask as an integer """
    return (0xffffffff << (32 - self.cidr)) & 0xffffffff

  def get_wildcard(self) -> IPBase:
    """ Returns mask wildcard """
    return IPBase(ip_int_to_str(~self.address & 0xffffffff))

  @staticmethod
  def get_netcidr(mask: str) -> int:
    """ Static method to return CIDR notation for a given mask """
    if mask not in IPv4Mask.get_valid_mask():
      raise ValueError(f"Invalid mask provided: {mask}")

    base = IPBase(mask)
    return ''.join(base.to_binary_array()).count('1')

  @staticmethod
  def get_valid_mask():
    return [ IPv4Mask.get_netmask(x) for x in range(1, 33) ]

  @staticmethod
  def get_netmask(network_length: int) -> str:
    """ Static method to return an ipv4 mask based on a network length """
    if not type(network_length) is int:
      raise ValueError("Network length must be an integer")
      
    if not 0 < network_length < 33:
      raise ValueError("Network length value must be between 1 and 32!")
    
    mask = (0xffffffff >> (32 - network_length)) << (32 - network_length)
    return (str( (0xff000000 & mask) >> 24) + '.' +
            str( (0x00ff0000 & mask) >> 16) + '.' +
            str( (0x0000ff00 & mask) >> 8)  + '.' +
            str( (0x000000ff & mask)))


class IPv4(IPBase):
  """ Simple Class providing tools to manipulate IPv4 addresses """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, address: str, mask: Union[int, str, IPv4Mask] = None):
    """ Constructor """
    
    net = None
    if "/" in address:
      address, net = address.split("/")
      net = int(net)

    super().__init__(address)

    if net is not None and mask is None:
      mask = net

    if mask is not None:
      if not isinstance(mask, IPv4Mask):
        mask = IPv4Mask(mask)

    self.mask: IPv4Mask = mask

    self.ports = []

  # ****************************************************************
  # Methods

  def get_mask(self) -> IPv4Mask:
    """ Getter for ip mask instance """
    return self.mask

  def get_port_numbers(self) -> List[int]:
    """ Getter for the Port numbers """
    return [p.get_number() for p in self.ports]

  def get_port_strings(self) -> List[int]:
    """ Getter for the Port strings """
    return [p.to_string() for p in self.ports]

  def set_mask(self, mask: Union[int, str, IPv4Mask]):
    """ Setter for ip mask """
    if not isinstance(mask, IPv4Mask):
      mask = IPv4Mask(mask)

    self.mask = mask

  def set_open_ports(self, ports: List[int] | List[Port]):
    """ Set the open ports """
    # Clear the list of open ports
    self.ports.clear()

    for p in ports:
      self.append_open_port(p)

  def get_net_addr(self) -> "IPv4":
    """ Returns network address for given IP """
    return IPv4(address=ip_int_to_str(self.address & self.mask.get_address()), mask=self.mask)

  def is_port_in_list(self, port: Union[int, Port]) -> bool:
    """ Check if the given port is in the list of ports """
    port_number = port

    if isinstance(port, Port):
      port_number = port.get_number()

    return port_number in self.get_port_numbers()

  def append_open_port(self, port: Union[int, Port]):
    """ Append the port to the list of open ports """
    is_port = isinstance(port, Port)
    is_number = isinstance(port, int)

    if not (is_port or is_number):
      raise ValueError(
          "Provided port must be an instance of class Port or an integer")

    if not self.is_port_in_list(port):
      if is_number:
        port = Port(port_number=port)

      self.ports.append(port)

    else:
      print(f"{port} is already in the list of open ports")

  def remove_port(self, port: int):
    """ Remove the port from the list of open ports """
    index = self.get_port_numbers().index(port)

    del self.ports[index]

  def is_in_subnet(self, net_addr: str) -> bool:
    """ Checks if the current ip is in the provided subnet """
    if "/" not in net_addr:
      raise ValueError(f"Invalid net address provided: {net_addr} ! Please include a net mask as CIDR notation")

    net = IPv4(net_addr)
    mask = net.get_mask().to_int()
    return (self.to_int() & mask) == (net.to_int() & mask)

  def __str__(self, show_mask: bool = True) -> str:
    """ Returns the current instance as a string """
    ip_str = super().__str__()

    if self.mask and show_mask:
      ip_str += f"/{self.mask.get_cidr()}"

    return ip_str
