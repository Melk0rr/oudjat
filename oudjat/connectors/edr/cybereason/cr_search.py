from enum import Enum

class CybereasonSearchFilters(Enum):
  """ Samples of Cybereason search filters """
  MALWARE_KNOWN = [
    {
      "fieldName": "type",
      "operator": "Equals",
      "values":["KnownMalware"]
    }
  ]

class CybereasonSearchSorts(Enum):
  """ Samples of possible Cybereason search """
  NEWEST_TO_OLDEST = {
    "sortingFieldName": "timestamp",
    "sortDirection": "DESC"
  }

  OLDEST_TO_NEWEST = {
    "sortingFieldName": "timestamp",
    "sortDirection": "ASC"
  }