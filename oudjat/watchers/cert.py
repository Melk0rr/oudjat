import requests
import json

from os.path import abspath, dirname, join
from bs4 import BeautifulSoup

from oudjat.utils.color_print import ColorPrint

this_dir = abspath(dirname(__file__))

def get_alert_tags(watcher):
    tag = watcher['tag']
    
    page = requests.get(watcher['url'])
    soup = BeautifulSoup(page.content, watcher['parser'])

    return soup.find_all(tag['name'], attrs=tag['attrs'])


def get_alerts():
    with open(join(this_dir, "cert.conf.json")) as f: data = json.load(f)

    res = {}
    for watcher in data:
        res[watcher['url']] = get_alert_tags(watcher)

    return res

def get_alert_details(alert):
    ColorPrint.yellow("Retreiving alert details...")
    # Todo