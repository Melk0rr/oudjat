import json
import math
import requests

from urllib import parse
from typing import List, Dict
from datetime import datetime, timedelta

from oudjat.utils.file import export_csv
from oudjat.utils.convertions import unixtime_to_str
from oudjat.connectors.edr.cybereason.cr_search_types import CybereasonEndpoints

class CybereasonEntry(dict):
  """ Cybereason entry dict """

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
    self.target = parse.urlparse(target)

    self.base_url = f"https://{target.netloc}:{port}"
    self.login_url = f"{base_url}/login.html"

    self.credentials = { "user": user, "password": password }
    
    self.session = None
    
  def connect() -> None:
    """ Connects to API using connector parameters """
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    session = requests.session()
    
    try:
      response = session.post(self.login_url, data=self.credentials, headers=headers, verify=True)
      
    except requests.exceptions.RequestException as e:
      raise(
        f"An error occured while trying to connect to Cybereason API at {self.target}: {e}"
      )
    
    self.session = session

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
    
    api_headers = {'Content-Type':'application/json'}
    api_resp = self.session.request(
      method=endpoint.value.get("method"),
      url=endpoint.value.get("endpoint"),
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
    search_type: str,
    search_filter: List[Dict] = None,
    limit: int = None,
    **kwargs
  ) -> List[Dict]:
    """ Runs search in API """

    if self.session is None:
      raise ConnectionError(
        f"You must initiate connection to {self.target.netloc} before running search !"
      )

    search_type = search_type.upper()
    endpoint_attr = CybereasonEndpoints[search_type]
    endpoint_search_limit = endpoint_attr.value.get("limit")

    if limit is None or limit > endpoint_search_limit:
      limit = endpoint_search_limit

    offset_mult = math.ceil(limit / endpoint_search_limit)

    res = []
    for i in range(0, offset_mult):
      res.extend(
        self.endpoint_search(
          search_type=endpoint_attr,
          search_filter=search_filter,
          limit=limit,
          offset=i,
          **kwargs
        )
      )
    
    return res