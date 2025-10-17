"""
A helper module that gather LDAP utility functions and variables.
"""

import re


def parse_dn(dn: str) -> dict[str, list[str]]:
    """
    Parse a DN into pieces.

    Args:
        dn (str) : distinguished name to parse

    Returns:
        dict[str, list[str]] : dictionary of dn pieces (CN, OU, DC)
    """

    pieces: dict[str, list[str]] = {}
    for dn_part in re.split(r",(?! )", dn):
        part_type, part_value = dn_part.split("=")

        if part_type not in pieces.keys():
            pieces[part_type] = list()

        pieces[part_type].append(part_value)

    return pieces

