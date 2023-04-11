""" Dictionary utils """
from enum import Enum


def join_dictionary_items(dictionary, char):
  """ Join dictionary items with the provided character """
  return char.join(f"{k}: {v}" for k, v in dictionary.items())


def join_dictionary_values(dictionary, char):
  """ Join dictionary values with the provided character """
  return char.join(f"{v}" for v in dictionary.values())
