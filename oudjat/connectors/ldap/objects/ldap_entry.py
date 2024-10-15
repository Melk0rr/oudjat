from typing import Any

class LDAPEntry(dict):
  """ LDAP entry dict """

  def get_dn(self) -> str:
    """ Retreive entry dn """
    return self.__getitem__("dn")

  def get(self, key: str, default_value: Any = None) -> Any:
    """ Retreive the value of the given attribute """
    if key not in self.__getitem__("attributes").keys():
      return default_value

    item = self.__getitem__("attributes").__getitem__(key)

    if isinstance(item, list) and len(item) == 0:
      return None

    return item

  def set(self, key: str, value: Any) -> Any:
    """ Set the given value of the provided attribute """
    return self.__getitem__("attributes").__setitem__(key, value)

  def get_raw(self, key: str) -> Any:
    """ Retreive the value of the given raw attribute """
    if key not in self.__getitem__("raw_attributes").keys():
      return None

    return self.__getitem__("raw_attributes").__getitem__(key)

  def attr(self):
    """ Retreive ldap attributes """
    return self.__getitem__("attributes")