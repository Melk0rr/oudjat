from typing import List

def b_not(b: bytes) -> bytes:
  """ Byte NOT """
  return int.to_bytes(~int.from_bytes(b, "big") & 0xff)

def b_and(b1: bytes, b2: bytes) -> bytes:
  """ Byte AND """
  res_int = int.from_bytes(b1, "big") & int.from_bytes(b2, "big")
  return res_int.to_bytes(max(len(b1), len(b2)), "big")

def b_or(b1: bytes, b2: bytes) -> bytes:
  """ Byte OR """
  res_int = int.from_bytes(b1, "big") | int.from_bytes(b2, "big")
  return res_int.to_bytes(max(len(b1), len(b2)), "big")

def b_xor(b1: bytes, b2: bytes) -> bytes:
  """ Byte XOR """
  res_int = int.from_bytes(b1, "big") ^ int.from_bytes(b2, "big")
  return res_int.to_bytes(max(len(b1), len(b2)), "big")

def bytes_2_int(b: List[bytes]) -> int:
  """ Converts a byte array into an int """
  return (
    (int.from_bytes(b[0]) << 24) + 
    (int.from_bytes(b[1]) << 16) + 
    (int.from_bytes(b[2]) << 8)  + int.from_bytes(b[3])
  )

def int_2_bytes(v: int) -> List[bytes]:
  """ Converts an int into an array of bytes """
  return [ (v >> 24) & 0xff, (v >> 16) & 0xff, (v >> 8) & 0xff, v & 0xff ]

def byte_2_bin(b: bytes) -> bin:
  """ Converts a byte into bin """
  return bin(int(b.hex(), base=16))[2:].zfill(8)

def ipstr_2_bytes(ip_str: str) -> List[bytes]:
  """ Converts an ip string into a byte array """
  
  addr_split = ip_str.split('.')
  if len(addr_split) != 4:
    raise ValueError(f"Invalid IP address provided: {ip_str}")

  return [ (int(x)).to_bytes(1, byteorder="little") for x in addr_split ]

def bytes_2_ipstr(b_array: List[bytes]) -> str:
  """ Converts a byte array into an ip string  """
  return '.'.join(f"{int.from_bytes(b, "big")}" for b in b_array)