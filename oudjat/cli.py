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

def main():

    print("""
     .d88888b.                888  d8b          888    
    d88P" "Y88b               888  Y8P          888    
    888     888               888               888    
    888     888 888  888  .d88888 8888  8888b.  888888 
    888     888 888  888 d88" 888 "888     "88b 888    
    888     888 888  888 888  888  888 .d888888 888    
    Y88b. .d88P Y88b 888 Y88b 888  888 888  888 Y88b.  
     "Y88888P"   "Y88888  "Y88888  888 "Y888888  "Y888 
                                   888                 
                                  d88P                 
                                888P"                  
    """)