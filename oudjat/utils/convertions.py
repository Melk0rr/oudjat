from typing import Union
from functools import reduce
from datetime import datetime, timedelta

def seconds_to_str(t: float) -> str:
  return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])

def unixtime_to_str(unix_time: Union[int, str], delta: int = 1) -> str:
	""" Converts a unix time string to readable string """
	date = datetime.utcfromtimestamp(int(unix_time) / 1000) + timedelta(hours=delta)
	return date.strftime('%Y-%m-%d %H:%M:%S')

def days_diff(date: datetime, reverse: bool = False) -> int:
  """ Returns difference between today and a past date """
  if date is not None:
    today = datetime.now()
    if reverse:
    	diff = date - today

    else:
      diff = today - date
      
    return diff.days
  
  return -1