from enum import Enum

class MSExchFlag(Enum):
  """ Flags to exploit user account control """
  UserMailbox = 1
  LinkedMailbox = 2
  SharedMailbox = 4
  LegacyMailbox = 8
  RoomMailbox = 16
  EquipmentMailbox = 32
  MailContact = 64
  MailUser = 128
  DistributionGroup = 256
  DynamicDistributionGroup = 512
  MailPublicFolder = 1024
  UniversalDistributionGroup = 2048
  UniversalSecurityGroup = 4096
  NonUniversalGroup = 8192
  MailRecipient = 16384
  User = 32768
  Contact = 65536
  Group = 131072
  DiscoveryMailbox = 262144
  RoleGroup = 524288
  PublicFolderMailbox = 1048576
  ArchiveMailbox = 2097152
  AuditLo = 8388608
  AuxAuditLo = 16777216
  SupervisoryRevie = 33554432
  RemoteUserMailbox = 2147483648
  RemoteDistributionGroup = 4294967296
  RemoteRoomMailbox = 8589934592
  RemoteEquipmentMailbox = 17179869184
  RemoteSharedMailbox = 34359738368

def check_account_flag(value: int, flag: LDAPAccountFlag) -> int:
	""" Compare given value to the chosen flag """
	return value & flag.value
