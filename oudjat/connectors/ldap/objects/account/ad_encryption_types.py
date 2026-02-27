"""
A simple module to enumerate AD encryption types.

See : https://learn.microsoft.com/fr-fr/troubleshoot/windows-server/active-directory/useraccountcontrol-manipulate-account-properties
"""

from oudjat.utils.bit_flag import BitFlag


class ADEncryptionType(BitFlag):
    """Bit flag to compare to the AD msDS-SupportedEncryptionTypes attribute."""

    UNDEFINED = 0
    DES_CBC_CRC = 1
    DES_CBC_MD5 = 2
    RC4 = 4
    AES_128 = 8
    AES_256 = 16
