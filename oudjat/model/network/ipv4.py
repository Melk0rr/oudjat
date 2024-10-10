""" IPv4 module """
from typing import List, Union

from . import Port

class IPv4Base:

  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, addr: str):
    """ Constructor """

    addr_split = addr.split('.')
    if len(addr_split) != 4:
      raise ValueError(f"Invalid IP address provided: {addr}")

    self.address: str = addr  
    self.bytes: List[bytes] = [ (int(x)).to_bytes(1, byteorder="little") for x in addr_split ]

  # ****************************************************************
  # Methods

  def get_address(self) -> str:
    """ Getter for ip string address """
    return self.address

  def get_bytes(self) -> List[bytes]:
    """ Getter for ip byte array """
    return self.bytes

  def to_hex_array(self) -> List[hex]:
    """ Returns the current ip as hex array """
    return [ x.hex() for x in self.bytes ]

  def to_hex_str(self) -> str:
    """ Returns the current ip as hex string """
    return ''.join(self.to_hex_array())

  def to_binary_array(self) -> List[bin]:
    """ Returns the current ip as a binary table """
    return [ bin(int(x, base=16))[2:] for x in self.to_hex_array() ]

  def to_int(self) -> int:
    """ Returns the current ip as an integer """
    return int(self.to_hex_str(), 16)


class IPv4Mask(IPv4Base):
  """ Simple Class providing tools to manipulate IPv4 mask """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, mask: int | str):
    """ Constructor """

    if type(mask) is str:
      super().__init__(mask)
      cidr = ''.join(self.to_binary_array()).count('1')
      
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

  def to_int(self) -> int:
    """ Returns the current mask as an integer """
    return (0xffffffff << (32 - self.cidr)) & 0xffffffff

  @staticmethod
  def get_netcidr(mask: str) -> int:
    """ Static method to return CIDR notation for a given mask """
    if mask not in IPv4Mask.get_valid_mask():
      raise ValueError(f"Invalid mask provided: {mask}")

    base = IPv4Base(mask)
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


class IPv4(IPv4Base):
  """ Simple Class providing tools to manipulate IPv4 addresses """

  # ****************************************************************
  # Attributes & Constructors

  def __init__(self, address: str, mask: str = None):
    """ Constructor """
    
    net = mask
    if "/" in address:
      address, net = address.split("/")

    super().__init__(address)

    if net:
      self.mask = IPv4Mask(int(net))

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

  def set_mask(self, mask: Union[int, str]):
    """ Setter for ip mask """
    self.mask = IPv4Mask(mask)

  def set_open_ports(self, ports: List[int] | List[Port]):
    """ Set the open ports """
    # Clear the list of open ports
    self.ports.clear()

    for p in ports:
      self.append_open_port(p)

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

  def is_in_subnet(self, net_addr: Union[str, IPv4]) -> bool:
    """ Checks if the current ip is in the provided subnet """
    if "/" not in net_addr:
      raise ValueError(f"Invalid net address provided: {net_addr} ! Please include a net mask as CIDR notation")

    net = IPv4(net_addr)
    mask = net.get_mask().to_int()
    return (self.to_int() & mask) == (net.to_int() & mask)

  def to_string(self, show_mask: bool = True) -> str:
    """ Returns the current instance as a string """
    ip_str = self.address

    if self.mask and show_mask:
      ip_str += f"/{self.mask.get_cidr()}"

    return ip_str
