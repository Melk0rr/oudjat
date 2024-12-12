""" Dictionary utils """
from typing import List, Dict

def join_dictionary_items(dictionary: Dict, char: str) -> str:
  """ Join dictionary items with the provided character """
  return char.join(f"{k}: {v}" for k, v in dictionary.items())

def join_dictionary_values(dictionary: Dict, char: str) -> str:
  """ Join dictionary values with the provided character """
  return char.join(f"{v}" for v in dictionary.values())

def map_list_to_dict(list_to_map: List, key: str) -> Dict:
  """ Maps a list into a dictionary using the provided key """
  return { el[key]: el for el in list_to_map }