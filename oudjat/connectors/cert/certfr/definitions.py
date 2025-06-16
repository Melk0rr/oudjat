"""Module hosting package global variables."""

from .certfr_page_types import CERTFRPageType

REF_TYPES = "|".join([pt.name for pt in CERTFRPageType])
LINK_TYPES = "|".join([pt.value for pt in CERTFRPageType])
CERTFR_REF_REGEX = rf"CERTFR-\d{{4}}-(?:{REF_TYPES})-\d{{3,4}}"
CERTFR_LINK_REGEX = rf"https:\/\/www\.cert\.ssi\.gouv\.fr\/(?:{LINK_TYPES})\/{CERTFR_REF_REGEX}"
