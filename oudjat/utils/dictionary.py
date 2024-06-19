""" Dictionary utils """
from typing import Dict

def join_dictionary_items(dictionary: Dict, char: str) -> str:
  """ Join dictionary items with the provided character """
  return char.join(f"{k}: {v}" for k, v in dictionary.items())


def join_dictionary_values(dictionary: Dict, char: str) -> str:
  """ Join dictionary values with the provided character """
  return char.join(f"{v}" for v in dictionary.values())
