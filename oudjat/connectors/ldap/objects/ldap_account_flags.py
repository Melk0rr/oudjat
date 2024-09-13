from enum import Enum

class LDAPAccountFlag(Enum):
	""" Flags to exploit user account control """
	ACCOUNT_DISABLE = 2
	HOMEDIR_REQUIRED = 8
	LOCKOUT = 16
	PASSWD_NOTREQD = 32
	PASSWD_CANT_CHANGE = 64
	ENCRYPTED_TEXT_PASSWORD_ALLOWED = 128
	NORMAL_ACCOUNT = 512
	INTERDOMAIN_TRUST_ACCOUNT = 2048
	WORKSTATION_TRUST_ACCOUNT = 4096
	SERVER_TRUST_ACCOUNT = 8192
	PASSWD_DONT_EXPIRE = 65536
	MNS_LOGON_ACCOUNT = 131072
	SMARTCARD_REQUIRED = 262144
	TRUSTED_FOR_DELEGATION = 524288
	NOT_DELEGATED = 1048576
	USE_DES_KEY_ONLY = 2097152
	DONT_REQUIRE_PREAUTH = 4194304
	PASSWORD_EXPIRED = 8388608
	TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION = 16777216
	NO_AUTH_DATA_REQUIRED = 33554432
	PARTIAL_SECRETS_ACCOUNT = 67108864

def check_flag(account_control: int, flag: LDAPAccountFlag) -> int:
	""" Compare given account control to the chosen LDAP flag """
	return account_control & flag.value

def is_disabled(account_control: int) -> bool:
	""" Checks if an account is disabled based on its account control """
	return check_flag(account_control, LDAPAccountFlag.ACCOUNT_DISABLE) > 0

def pwd_expires(account_control: int) -> bool:
	""" Checks if the account's password expires """
	return check_flag(account_control, LDAPAccountFlag.PASSWD_DONT_EXPIRE) == 0