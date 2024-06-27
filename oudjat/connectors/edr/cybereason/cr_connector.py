import re
import json
import math
import urllib
import requests

from urllib.parse import urlparse
from typing import List, Dict, Any
from datetime import datetime, timedelta

from oudjat.utils.file import export_csv
from oudjat.utils.color_print import ColorPrint
from oudjat.utils.convertions import unixtime_to_str
from oudjat.connectors.edr.cybereason.cr_endpoints import CybereasonEndpoints

class CybereasonEntry(dict):
  """ Cybereason entry dict """

  def __init__(self, entry_type: "CybereasonEndpoints", **kwargs):
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

class CybereasonConnector:
  """ Cybereason connector to interact and query Cybereason API """

  def __init__(
    self,
    target: str,
    user: str,
    password: str,
    port: int = 443
  ):
    """ Constructor """
    self.port = port
    
    scheme = "http"
    if self.port == 443:
      scheme += "s"
      
    # Inject protocol if not found
    if not re.match(r'http(s?):', target):
      target = f"{scheme}://{target}"

    self.target = urlparse(target)
    self.base_url = f"{self.target.scheme}://{self.target.netloc}:{port}"
    self.login_url = f"{self.base_url}/login.html"

    self.credentials = { "username": user, "password": password }
    
    self.session = None
    
  def connect(self) -> None:
    """ Connects to API using connector parameters """
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    session = requests.session()
    
    try:
      response = session.post(self.login_url, data=self.credentials, headers=headers, verify=True)
      
    except ConnectionError as e:
      raise(
        f"An error occured while trying to connect to Cybereason API at {self.target}: {e}"
      )
    
    ColorPrint.green(f"Connected to {self.target.netloc}:{self.port}")
    self.session = session

  def disconnect(self) -> None:
    """ Close session with target """
    self.session.close()

  def endpoint_search(
    self,
    endpoint: "CybereasonEndpoints",
    limit: int,
    offset: int = 0,
    search_filter: List[Dict] = None,
    **kwargs
  ) -> List[Dict]:
    """ Runs search in specific endpoint """
    
    filter_opt = {}
    if search_filter is not None:
      filter_opt["filters"] = search_filter

    query = json.dumps({
      "limit": limit,
      "offset": offset,
      **filter_opt,
      **kwargs
    })

    endpoint_url = f"{self.base_url}{endpoint.value.get('endpoint')}"
    
    api_headers = {'Content-Type':'application/json'}
    api_resp = self.session.request(
      method=endpoint.value.get("method"),
      url=endpoint_url,
      data=query,
      headers=api_headers
    )
    
    res = []
    if api_resp.content:
      res = json.loads(api_resp.content)
      
      # Handling CR nonesense
      if res.get("data") is not None:
        res = res.get("data")

      if res.get(endpoint.name.lower()) is not None:
        res = res.get(endpoint.name.lower())
    
    return res

  def search(
    self,
    endpoint: str,
    search_filter: List[Dict] = None,
    limit: int = None,
    **kwargs
  ) -> List["CybereasonEntry"]:
    """ Runs search in API """

    if self.session is None:
      raise ConnectionError(
        f"You must initiate connection to {self.target.netloc} before running search !"
      )

    endpoint = endpoint.upper()
    if endpoint not in CybereasonEndpoints.__members__:
      raise(f"Invalid Cybereason endpoint provided: {endpoint}")

    endpoint_attr = CybereasonEndpoints[endpoint]
    endpoint_search_limit = endpoint_attr.value.get("limit")

    # Set search limit
    if limit is None or limit > endpoint_search_limit:
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
      
      res.extend(search_i)

    print(f"{len(res)} {endpoint_attr.name.lower()} found")

    entries = list(
      map(
        lambda entry: CybereasonEntry(entry_type=endpoint_attr, **entry),
        res
      )
    )

    return entries