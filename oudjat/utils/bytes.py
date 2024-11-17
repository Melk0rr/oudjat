from typing import List

def i_not(val: int) -> int:
  """ Byte NOT """
  return ~val & 0xffffffff

def i_and(val1: int, val2: int) -> int:
  """ Byte AND """
  return val1 & val2

def i_or(val1: int, val2: int) -> int:
  """ Byte OR """
  return val1 | val2

def i_xor(val1: int, val2: int) -> int:
  """ Byte XOR """
  return val1 ^ val2

def count_1_bits(val: int) -> int:
  """ Counts the number of bits with 1 value in an integer """
  return bin(val).count('1')
