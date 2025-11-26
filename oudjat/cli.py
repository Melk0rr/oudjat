"""
A SOC toolbox and maybe more if I have the time.

Usage:
    oudjat -h | --help
    oudjat -l=LOGGING | --log=LOGLEVEL
    oudjat -V | --version

Commands

Options:
    -a --append                     append to the output file
    -c --config=CONFIG              specify config file
    -f --file                       set target (reads from file, one domain per line)
    -h --help                       show this help message and exit
    -l --log=LOGLEVEL               specify the log level
    -o --output=FILENAME            save execution logs to the specified file
    -S --silent                     simple output, one per line
    -t --target                     set target (comma separated, no spaces, if multiple)
    -v --verbose                    print debug info and full request output
    -V --version                    show version and exit
    -x --export-csv=CSV             save results as csv

Cert-options:
    --feed                          run cert mode from a feed
    --filter=FILTER                 date filter to apply with feed option (e.g. 2023-03-10)
    --keywords=KEYWORDS             set keywords to track (comma separated, no spaces, if multiple)
    --keywordfile=KEYWORDFILE       set keywords to track (file, one keyword per line)

Exemples:
    oudjat cert -t https://cert.ssi.gouv.fr/alerte/feed/ --feed --filter "2023-03-13"
    oudjat cert -f ./tests/certfr.txt --export-csv ./tests/certfr_20230315.csv --keywordfile ./tests/keywords.txt
    oudjat vuln -f ./tests/cve.txt --export-csv ./tests/cve_20230313.csv

Help:
    For help using this tool, please open an issue on the Github repository:
    https://github.com/Melk0rr/Oudjat
"""

import logging
import sys
import time
from typing import Any

from docopt import docopt

import oudjat.commands
from oudjat.banner import banner
from oudjat.utils import ColorPrint, StdOutHook, TimeConverter
from oudjat.utils.logging import oudjatLogger

from . import __version__ as VERSION


def config_logging(options: dict[str, str]) -> "logging.Logger":
    """
    Set the logging level.

    Args:
        options (dict[str, str]): CLI options
    """

    LOGGING_LEVELS = {
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
        "DEBUG": logging.DEBUG,
    }

    return oudjatLogger(level=LOGGING_LEVELS.get(options["--log"], LOGGING_LEVELS["INFO"]))


def command_switch(options: dict[str, str]) -> Any:
    """
    Script command switch case.

    Args:
        options (dict[str, str]): CLI options
    """

    COMMAND_OPTIONS = {}

    command_name = next(command for command in COMMAND_OPTIONS.keys() if options[command])
    return COMMAND_OPTIONS[command_name](options)


def main() -> None:
    """
    Program entry point that runs each time the 'oudjat' command line is executed.
    """

    try:
        if sys.version_info < (3, 0):
            sys.stdout.write("Sorry, requires Python 3.x\n")
            sys.exit(1)

        start_time = time.time()
        options = docopt(__doc__, version=VERSION)

        original_stdout = sys.stdout

        logger = config_logging(options)

        if options["--output"] and options["--silent"]:
            sys.stdout = StdOutHook(options["FILENAME"], options["--silent"], options["--output"])

        if not options["--target"] and not options["--file"] and not options["--directory"]:
            logger.error("Target required! Use -h to see usage. Either -f or -t")
            return

        if options["--target"] and options["--file"]:
            logger.error("Please only supply one target method - either -f or -t.")
            return

        ColorPrint.blue(banner)

        command = command_switch(options)
        command.run()

        logger.info(f"Oudjat runtime -  {TimeConverter.seconds_to_str(time.time() - start_time)}s")

        sys.stdout = original_stdout

    except KeyboardInterrupt:
        print("\nQuitting...")
        sys.exit(0)
