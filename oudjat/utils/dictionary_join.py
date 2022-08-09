"""
  Join dictionary items with the provided character
"""
def join_dictionary_items(dictionary, char):
  return char.join("{} : {}".format(k, v) for k, v in dictionary.items())

"""
  Join dictionary values with the provided character
"""
def join_dictionary_values(dictionary, char):
  return char.join("'{}'".format(v) for v in dictionary.values())