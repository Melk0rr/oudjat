import re
import json
import math
import requests

from urllib.parse import urlparse
from typing import List, Dict, Union

from oudjat.utils import ColorPrint
from oudjat.utils import unixtime_to_str

from oudjat.connectors import Connector
from oudjat.connectors.edr.cybereason import CybereasonEndpoint

class CybereasonEntry(dict):
  """ Cybereason entry dict """

  def __init__(self, entry_type: "CybereasonEndpoint", **kwargs):
    """ Constructor """

    self.type = entry_type
    cleaned_kwargs = {}
    entry_attrs = entry_type.value.get("attributes")
    
    for k, v in kwargs.items():
      if k in entry_attrs:

        # Handle unix time
        if "time" in k.lower():
          v = unixtime_to_str(v)

        # Add short policy version
        if k == "policyName":
          cleaned_kwargs["policyShort"] = v
          shortPolicy = re.search(r'Detect|Protect', v)
          
          if shortPolicy is not None:
            cleaned_kwargs["policyShort"] = shortPolicy.group(0)
            
        # Handle malware file path
        if k == "malwareDataModel":
          cleaned_kwargs["filePath"] = v.get("filePath", None)
        
        cleaned_kwargs[k] = v

    dict.__init__(self, **cleaned_kwargs)

class CybereasonConnector(Connector):
  """ Cybereason connector to interact and query Cybereason API """

  def __init__(
    self,
    target: str,
    service_name: str = "OudjatCybereasonAPI",
    port: int = 443
  ):
    """ Constructor """
    
    scheme = "http"
    if port == 443:
      scheme += "s"
      
    # Inject protocol if not found
    if not re.match(r'http(s?):', target):
      target = f"{scheme}://{target}"

    super().__init__(target=urlparse(target), service_name=service_name, use_credentials=True)

    self.target = urlparse(f"{self.target.scheme}://{self.target.netloc}:{port}")

    
  def connect(self) -> None:
    """ Connects to API using connector parameters """
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    session = requests.session()
    
    try:
      creds = { "username": self.credentials.username, "password": self.credentials.password }
      session.post(f"{self.target.geturl()}/login.html", data=creds, headers=headers, verify=True)
      
    except ConnectionError as e:
      raise(
        f"An error occured while trying to connect to Cybereason API at {self.target}: {e}"
      )
    
    ColorPrint.green(f"Connected to {self.target.netloc}")
    self.connection = session

  def disconnect(self) -> None:
    """ Close session with target """
    self.connection.close()

  def endpoint_search(
    self,
    endpoint: "CybereasonEndpoint",
    limit: int = None,
    offset: int = 0,
    search_filter: List[Dict] = None,
    **kwargs
  ) -> List[Dict]:
    """ Runs search in specific endpoint """
    
    filter_opt = {
      "filters": []
    }
    if search_filter is not None:
      filter_opt["filters"] = search_filter

    query_content = {
      "limit": limit,
      "offset": offset,
      **filter_opt,
      **kwargs
    }
    query = json.dumps(query_content)

    endpoint_url = f"{self.target.geturl()}{endpoint.value.get("endpoint")}"
    
    api_headers = {'Content-Type':'application/json'}
    api_resp = self.connection.request(
      method=endpoint.value.get("method"),
      url=endpoint_url,
      data=query,
      headers=api_headers
    )
    
    res = []
    try:
      if api_resp.content:
        res = json.loads(api_resp.content)
        
        # Handling CR nonesense
        if not isinstance(res, list):
          if "data" in res:
            if res.get("data") is None:
              return None

            res = res.get("data")
    
          if res.get(endpoint.name.lower()) is not None:
            res = res.get(endpoint.name.lower())

    except Exception as e:
      ColorPrint.red(f"An error occured while querying {endpoint.value.get('endpoint')}\n{e}")

    return res

  def search(
    self,
    endpoint: str,
    search_filter: List[Dict] = None,
    limit: int = None,
    **kwargs
  ) -> List["CybereasonEntry"]:
    """ Runs search in API """

    if self.connection is None:
      raise ConnectionError(
        f"You must initiate connection to {self.target.netloc} before running search !"
      )

    endpoint = endpoint.upper()
    if endpoint not in CybereasonEndpoint.__members__:
      raise ValueError(f"Invalid Cybereason endpoint provided: {endpoint}")

    endpoint_attr = CybereasonEndpoint[endpoint]
    endpoint_search_limit = endpoint_attr.value.get("limit")

    # Set search limit
    if limit is None:
      limit = endpoint_search_limit

    offset_mult = math.ceil(limit / endpoint_search_limit)

    res = []
    for i in range(0, offset_mult):
      search_i = self.endpoint_search(
        endpoint=endpoint_attr,
        search_filter=search_filter,
        limit=limit,
        offset=i,
        **kwargs
      )
      
      if search_i is not None:
        res.extend(search_i)

    print(f"{len(res)} {endpoint_attr.name.lower()} found")

    entries = list(
      map(
        lambda entry: CybereasonEntry(entry_type=endpoint_attr, **entry),
        res
      )
    )

    return entries

  def search_files(
    self,
    file_name: Union[str, List[str]],
    search_filter: List[Dict] = None,
    limit: int = None
  ) -> List["CybereasonEntry"]:
    """ Searches for specific file(s) """

    if not isinstance(file_name, list):
      file_name = [ file_name ]
      
    file_filters = [{ "fieldName": "fileName", "values": file_name, "operator": "Equals" }]
    # return self.search(endpoint="FILES", search_filter=search_filter, limit=limit, fileFilters=file_filters)
    
    if limit is None:
      limit = CybereasonEndpoint.FILES.value.get("limit")
      
    batch_search = self.endpoint_search(
      endpoint=CybereasonEndpoint.FILES,
      limit=limit,
      search_filter=search_filter
    )

    print(batch_search)