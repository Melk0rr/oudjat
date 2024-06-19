"""
Usage:
  oudjat cert (-t TARGET | -f FILE) [options]  [--check-max-cve] [--feed] [--filter=FILTER]
                                                [--keywords=KEYWORDS | --keywordfile=FILE]   
  oudjat vuln (-t TARGET | -f FILE) [options]
  oudjat kpi (-d DIRECTORY) (-s SOURCES) [options] [--config=CONFIG] [--history=HIST] [--history-gap=GAP]
  oudjat sc (-t TARGET | -f FILE) (--sc-url=SC_URL) [--sc-mode=SC_MODE]
  oudjat -h | --help
  oudjat -V | --version

Commands
  cert                            parse data from cert page
  kpi                             generates kpi
  vuln                            parse CVE data from Nist page
  
Options:
  -a --append                     append to the output file
  -c --config=CONFIG              specify config file
  -d --directory                  set target (reads from file, one domain per line)
  -f --file                       set target (reads from file, one domain per line)
  -h --help                       show this help message and exit
  -H --history=HIST               check kpis for last n element
  -l --cve-list=CVE_LIST          provide a list of cve to be used as a database and reduce the amount of requests
  -o --output=FILENAME            save to filename
  -s --sources=SOURCES            kpi source files
  -S --silent                     simple output, one per line
  -t --target                     set target (comma separated, no spaces, if multiple)
  -v --verbose                    print debug info and full request output
  -V --version                    show version and exit
  -x --export-csv=CSV             save results as csv
  --history-dates=DATES           gap between elements

Cert-options:
  --check-max-cve                 determine which CVE is the most severe based on the CVSS score
  --feed                          run cert mode from a feed
  --filter=FILTER                 date filter to apply with feed option (e.g. 2023-03-10)
  --keywords=KEYWORDS             set keywords to track (comma separated, no spaces, if multiple)
  --keywordfile=KEYWORDFILE       set keywords to track (file, one keyword per line)

Exemples:
  oudjat cert -t https://cert.ssi.gouv.fr/alerte/feed/ --feed --filter "2023-03-13" --check-max-cve
  oudjat cert -f ./tests/certfr.txt --export-csv ./tests/certfr_20230315.csv --keywordfile ./tests/keywords.txt --check-max-cve
  oudjat vuln -f ./tests/cve.txt --export-csv ./tests/cve_20230313.csv

Help:
  For help using this tool, please open an issue on the Github repository:
  https://github.com/Melk0rr/Oudjat
"""

import sys
import time

from docopt import docopt
from typing import Dict, Any

import oudjat.commands
from oudjat.banner import banner
from oudjat.utils.color_print import ColorPrint
from oudjat.utils.convertions import seconds_to_str
from oudjat.utils.stdouthook import StdOutHook

from . import __version__ as VERSION

COMMAND_OPTIONS = ["vuln", "cert", "sc", "kpi"]

def command_switch(options: Dict) -> Any:
  """ Script command switch case """
  
  switch = {
    "vuln": oudjat.commands.Vuln,
    "cert": oudjat.commands.Cert,
    "kpi" : oudjat.commands.KPIFactory
    # "sc"  : oudjat.commands.SC,
  }

  command_name = next(command for command in COMMAND_OPTIONS if options[command])
  return switch[command_name](options)

def main() -> None:
  """ Main program function """

  try:
    if sys.version_info < (3, 0):
      sys.stdout.write("Sorry, requires Python 3.x\n")
      sys.exit(1)

    start_time = time.time()

    options = docopt(__doc__, version=VERSION)

    if options["--output"] or options["--silent"]:
      sys.stdout = StdOutHook(
          options["FILENAME"], options["--silent"], options["--output"])

    if not options["--target"] and not options["--file"] and not options["--directory"]:
      ColorPrint.red(
          "Target required! Run with -h for usage instructions. Either -t target.host or -f file.txt required")
      return

    if options["--target"] and options["--file"]:
      ColorPrint.red(
          "Please only supply one target method - either read by file with -f or as an argument to -t.")
      return

    ColorPrint.blue(banner)

    command = command_switch(options)
    command.run()

    print(
        f"\nWatchers infos search took {seconds_to_str(time.time() - start_time)}s")

    if options["--output"]:
      sys.stdout.write_out()

  except KeyboardInterrupt:
    print("\nQuitting...")
    sys.exit(0)
