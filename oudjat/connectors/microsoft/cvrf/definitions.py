"""A module to centralize package global variables."""

CVRF_ID_REGEX = r"\d{4}-[a-zA-Z]{3}"
CVRF_PRODUCT_REGEX = r"\d{4,5}(?:-\d{4,5})?"
KB_NUM_REGEX = r"\d{7}"

API_BASE_URL = "https://api.msrc.microsoft.com/"
API_REQ_HEADERS = {"Accept": "application/json"}

