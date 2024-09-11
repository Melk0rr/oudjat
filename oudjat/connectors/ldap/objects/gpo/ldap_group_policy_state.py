from enum import Enum

class LDAPGroupPolicyState(Enum):
  ENABLED = 0
  DISABLED = 1
  ENFORCED = 2