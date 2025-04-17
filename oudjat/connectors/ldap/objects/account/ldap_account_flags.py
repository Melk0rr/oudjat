from enum import IntEnum


class LDAPAccountFlag(IntEnum):
    """
    Bit flag to exploit user account control
    """

    SCRIPT = 1
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

    @staticmethod
    def check_account_flag(account_control: int, flag: "LDAPAccountFlag") -> int:
        """
        Compares given value to the chosen flag.

        Args:
            account_control (int): The integer representation of account control flags.
            flag ("LDAPAccountFlag"): An enum-like class representing LDAP account control flags.

        Returns:
            int: The result of the bitwise AND operation between `account_control` and `flag`.
        """

        return account_control & flag

    @staticmethod
    def is_disabled(account_control: int) -> bool:
        """
        Checks if an account is disabled based on its account control.

        Args:
            account_control (int): The integer representation of account control flags.

        Returns:
            bool: True if the ACCOUNT_DISABLE flag is set, otherwise False.
        """

        return (
            LDAPAccountFlag.check_account_flag(account_control, LDAPAccountFlag.ACCOUNT_DISABLE)
            != 0
        )

    @staticmethod
    def pwd_expires(account_control: int) -> bool:
        """
        Checks if the account's password expires.

        Args:
            account_control (int): The integer representation of account control flags.

        Returns:
            bool: True if the PASSWD_DONT_EXPIRE flag is not set, otherwise False.
        """

        return not LDAPAccountFlag.check_account_flag(
            account_control, LDAPAccountFlag.PASSWD_DONT_EXPIRE
        )

    @staticmethod
    def pwd_expired(account_control: int) -> bool:
        """
        Checks if the account's password is expired.

        Args:
            account_control (int): The integer representation of account control flags.

        Returns:
            bool: True if the PASSWORD_EXPIRED flag is set, otherwise False.
        """

        return (
            LDAPAccountFlag.check_account_flag(account_control, LDAPAccountFlag.PASSWORD_EXPIRED)
            != 0
        )

    @staticmethod
    def pwd_required(account_control: int) -> bool:
        """
        Checks if the account requires a password.

        Args:
            account_control (int): The integer representation of account control flags.

        Returns:
            bool: True if the PASSWD_NOTREQD flag is not set, otherwise False.
        """

        return not LDAPAccountFlag.check_account_flag(
            account_control, LDAPAccountFlag.PASSWD_NOTREQD
        )

    @staticmethod
    def is_locked(account_control: int) -> bool:
        """
        Checks if the account is locked.

        Args:
            account_control (int): The integer representation of account control flags.

        Returns:
            bool: True if the LOCKOUT flag is set, otherwise False.
        """

        return not LDAPAccountFlag.check_account_flag(
            account_control, LDAPAccountFlag.LOCKOUT
        )

