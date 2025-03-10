from enum import Enum


class TSCAssetListType(Enum):
    """Enumerate asset list types"""

    COMBINATION = "combination"
    DNSNAME = "dnsname"
    DNSNAMEUPLOAD = "dnsnameupload"
    DYNAMIC = "dynamic"
    LDAPQUERY = "ldapquery"
    STATIC = "static"
    STATICEVENTFILTER = "staticeventfilter"
    STATICVULNFILTER = "staticfulnfilter"
    TEMPLATES = "templates"
    UPLOAD = "upload"
    WATCHLIST = "watchlist"
    WATCHLISTEVENTFILTER = "watchlisteventfilter"
    WATCHLISTUPLOAD = "watchlistupload"
