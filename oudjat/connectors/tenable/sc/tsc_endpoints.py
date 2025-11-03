"""
A helper module that lists Tenable.sc available methods/endpoints for the TSCConnector.
"""

from enum import Enum


class TSCEndpoint(Enum):
    """
    A helper enumeration to list possible TSCConnector actions.
    """

    VULNS = "vulns.list"
    REPOS = "repositories.list"
    SCANS = "scans.list"
    SCANS_CREATE = "scans.create"
    SCANS_DELETE = "scans.delete"
    SCANS_DETAILS = "scans.details"
    ASSETS = "asset_lists.list"
    ASSETS_CREATE = "asset_lists.create"
    ASSETS_DELETE = "asset_lists.delete"
    ASSETS_DETAILS = "asset_lists.details"

