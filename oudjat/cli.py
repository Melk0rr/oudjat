"""
Usage:
  oudjat (-u URL | -f FILE) [-o FILENAME]
  oudjat -h
  oudjat (--version | -V)
  
Options:
  -h --help                       show this help message and exit
  -t --target                     set target (comma separated, no spaces, if multiple)
  -f --file                       set target (reads from file, one domain per line)
  -o --output                     save to filename
  -i --additional-info            show additional information about the host from Shodan (requires API key)
  -S --silent                     only output subdomains, one per line
  -v --verbose                    print debug info and full request output
  -V --version                    show version and exit
Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/JaufreLallement/Oudjat
"""

from docopt import docopt

from oudjat.banner import banner
from oudjat.utils.color_print import ColorPrint

def main():

    ColorPrint.blue(banner)