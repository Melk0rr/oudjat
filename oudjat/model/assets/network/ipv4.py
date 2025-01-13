import re
import socket

from enum import Enum
from typing import List, Union

from oudjat.utils import ColorPrint, count_1_bits, i_not, i_and

from . import Port

def ip_str_to_int(ip: str) -> int:
  """ Converts an ip address string into an int """
  return int(''.join([bin(int(x)+256)[3:] for x in ip.split('.')]), 2)

def ip_int_to_str(ip: int) -> str:
  """ Converts an ip address integer into a string """
  return '.'.join([str((ip >> i) & 0xff) for i in (24, 16, 8, 0)])

def cidr_to_int(cidr: int) -> int:
  """ Returns a mask integer value based on the given network length """
  return (0xffffffff << (32 - cidr)) & 0xffffffff

class IPVersion(Enum):
  IPV4 = {
    "pattern": r'^(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$'
  }
  IPV6 = {
    "pattern": r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$'
  }


class IPv4:
  """ Simple Class providing tools to manipulate IPv4 addresses """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, address: Union[int, str]):
    """ Constructor """
    
    if type(address) is int:
      address = ip_int_to_str(address)

    if re.match(IPVersion.IPV4.value["pattern"], address):
      self.version = IPVersion.IPV4
    
    elif re.match(IPVersion.IPV6.value["pattern"], address):
      self.version = IPVersion.IPV6
    
    else:
      raise ValueError(f"Invalid IPv4 address provided: {address}")

    self.address: int = ip_str_to_int(address)

    self.ports = []

  # ****************************************************************
  # Methods

  def get_address(self) -> str:
    """ Getter for ip string address """
    return self.address

  def __int__(self) -> int:
    """ Converts the current ip base into an integer """
    return self.address

  def __str__(self) -> str:
    """ Converts the current ip base into a string """
    return ip_int_to_str(self.address)

  def get_port_numbers(self) -> List[int]:
    """ Getter for the Port numbers """
    return [ p.get_number() for p in self.ports ]

  def get_port_strings(self) -> List[int]:
    """ Getter for the Port strings """
    return [ str(p) for p in self.ports ]

  def set_open_ports(self, ports: Union[List[int], List[Port]]):
    """ Set the open ports """
    # Clear the list of open ports
    self.ports.clear()

    for p in ports:
      self.append_open_port(p)

  def get_net_addr(self) -> "IPv4":
    """ Returns network address for given IP """
    return IPv4(address=i_and(int(self.address), int(self.mask)), mask=self.mask)

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

  def is_in_subnet(self, net_addr: Union[int, str], mask) -> bool:
    """ Checks if the current ip is in the provided subnet """
    if "/" not in net_addr:
      raise ValueError(f"Invalid net address provided: {net_addr} ! Please include a net mask as CIDR notation")

    net = IPv4(address=net_addr)
    net_mask = int(net.get_mask())
    return (i_and(int(self) & net_mask)) == (int(net) & net_mask)

  def __str__(self, show_mask: bool = True) -> str:
    """ Returns the current instance as a string """
    ip_str = super().__str__()

    if self.mask and show_mask:
      ip_str += f"/{self.mask.get_cidr()}"

    return ip_str

  @staticmethod
  def resolve_from_hostname(hostname: str) -> str:
    """ Resolves the IP address for the current URL """
    ip = None
    try:
      ip = socket.gethostbyname(hostname)

    except Exception as e:
      ColorPrint.red(f"{hostname}: could not resolve IP address\n{e}")

    return ip


class IPv4Mask(IPv4):
  """ Simple Class providing tools to manipulate IPv4 mask """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, mask: Union[int, str] = None, cidr: int = None):
    """ Constructor """

    if mask is None and cidr is None:
      raise ValueError("Please provide either a CIDR mask or a mask value as integer or string")

    if cidr is not None:
      if not 1 < cidr < 33:
        raise ValueError("Mask CIDR value must be between 1 and 32!")

      mask = cidr_to_int(cidr)

    if type(mask) is not int and type(mask) is not str:
      raise ValueError(f"Invalid mask provided : {mask}. You must provide a string or an integer !")

    super().__init__(mask)
    self.cidr = count_1_bits(self.address)

  # ****************************************************************
  # Methods

  def get_cidr(self) -> int:
    """ Getter for mask CIDR """
    return self.cidr

  def cidr_to_int(self) -> int:
    """ Returns the current mask as an integer """
    return (0xffffffff << (32 - self.cidr)) & 0xffffffff

  def get_wildcard(self) -> IPv4:
    """ Returns mask wildcard """
    return IPv4(i_not(self.address))

  @staticmethod
  def get_netcidr(mask: str) -> int:
    """ Static method to return CIDR notation for a given mask """
    if mask not in IPv4Mask.get_valid_mask():
      raise ValueError(f"Invalid mask provided: {mask}")

    base = IPv4(mask)
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
    
    return ip_int_to_str(cidr_to_int(network_length))

