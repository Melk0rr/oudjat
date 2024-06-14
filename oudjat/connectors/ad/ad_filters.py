from enum import Enum

class ADSearchFilters(Enum):
	""" LDAP search filter enumeration by object type """

	user = "(&(objectClass=user)(!(objectClass=computer)))"
	computer = "(&(objectClass=computer)(!(objectClass=user)))"