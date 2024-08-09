################################################################################
# Useful content
CVE_REGEX = r'CVE-\d{4}-\d{4,7}'

CVRF_ID_REGEX = r'\d{4}-[a-zA-Z]{3}'
MS_PRODUCT_REGEX = r'\d{4,5}(?:-\d{4,5})?'
KB_NUM_REGEX = r'\d{7}'

API_BASE_URL = "https://api.msrc.microsoft.com/"
API_REQ_HEADERS = { 'Accept': 'application/json' }