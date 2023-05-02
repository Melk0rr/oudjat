"""
Usage:
  oudjat watch (-t TARGET | -f FILE) [options]  [--check-max-cve] [--feed] [--filter=FILTER]
                                                [--keywords=KEYWORDS | --keywordfile=FILE]   
  oudjat vuln (-t TARGET | -f FILE) [options]
  oudjat -h | --help
  oudjat -V | --version

Commands
  cert                            parse data from cert page
  vuln                             parse CVE data from Nist page

Options:
  -h --help                       show this help message and exit
  -t --target                     set target (comma separated, no spaces, if multiple)
  -f --file                       set target (reads from file, one domain per line)
  -o --output                     save to filename
  -S --silent                     simple output, one per line
  -v --verbose                    print debug info and full request output
  -V --version                    show version and exit
  --export-csv=CSV                save results as csv

CERT-options:
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

import oudjat.commands
from oudjat.banner import banner
from oudjat.utils.color_print import ColorPrint
from oudjat.utils.convertions import seconds_to_str
from oudjat.utils.stdouthook import StdOutHook

from . import __version__ as VERSION

COMMAND_OPTIONS = ["vuln", "watch"]

def command_switch(options):
  """ Script command switch case """
  
  switch = {
    "vuln": oudjat.commands.Vuln,
    "watch": oudjat.commands.Watch,
  }

  command_name = next(command for command in COMMAND_OPTIONS if options[command])
  print(command_name)
  return switch[command_name](options)

def main():
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

    if not options["--target"] and not options["--file"]:
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
