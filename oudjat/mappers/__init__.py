"""
A module dedicated to mapping assets mostly from connectors data.
"""

from .asset_mapper import AssetMapper
from .connectors.endoflife import EOLAssetMapper
from .connectors.ldap import LDAPAssetMapper

__all__ = [
    "AssetMapper",
    "EOLAssetMapper",
    "LDAPAssetMapper",
]
