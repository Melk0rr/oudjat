import requests
import re
from bs4 import BeautifulSoup

def parse_certfr_page(self, target):
  host = target["host"]
  if not re.match(r'http(s?):', host):
    host = 'http://' + target["host"]

  try:
    req = requests.get(host)
    soup = BeautifulSoup(req.content, 'html.parser')


  except Exception as e:
    self.handle_exception(e, f"Error while requesting {host}. Make sure the target is accessible")