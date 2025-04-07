from .certfr_page_types import CERTFRPageType

REF_TYPES = "|".join([pt.name for pt in CERTFRPageType])
LINK_TYPES = "|".join([pt.value for pt in CERTFRPageType])
CERTFR_REF_REGEX = rf"CERTFR-\d{{4}}-(?:{REF_TYPES})-\d{{3,4}}"
CERTFR_LINK_REGEX = rf"https:\/\/www\.cert\.ssi\.gouv\.fr\/(?:{LINK_TYPES})\/{CERTFR_REF_REGEX}"
URL_REGEX = r"http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
