"""
Oudjat main entry point.
"""

import logging
import sys
from datetime import datetime
from typing import Any

from docopt import docopt

from oudjat.banner import banner
from oudjat.commands.s1_connector_command import S1ConnectorCommand
from oudjat.utils import ColorPrint, Context, StdOutHook, TimeConverter
from oudjat.utils.logging import oudjatLogger

from . import __version__ as VERSION

_BASE_DOC = """
A SOC toolbox and maybe more if I have the time.

Usage:
    oudjat -h | --help
    oudjat -l=LOGGING | --log=LOGLEVEL
    oudjat -V | --version
"""

_OPT_DOC = """
Options:
    -a --append                       append to the output file
    -c --config=CONFIG                specify config file
    -f --file                         set target (reads from file, one domain per line)
    -h --help                         show this help message and exit
    -l --log=LOGLEVEL                 specify the log level
    -o --output=FILENAME              save execution logs to the specified file
    -p --password=PASS                password to use with the connector
    -S --silent                       simple output, one per line
    -t --target=TARGET                set target (comma separated, no spaces, if multiple)
    -u --username=USER                username to use with the connector
    -v --verbose                      print debug info and full request output
    -V --version                      show version and exit
    --creds-service=SERVICE           service name to retrieve the credentials from
    --csv=CSV                         save results as csv
    --json=JSON                       save results as json
"""

_HELP_DOC = """
Help:
    For help using this tool, please open an issue on the Github repository:
    https://codeberg.org/me1k0r/oudjat
"""

_COMMAND_OPTIONS = {"connectors.edr.sentinelone": S1ConnectorCommand}

def _config_logging(options: dict[str, str]) -> "logging.Logger":
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


def _command_switch(options: dict[str, str]) -> Any:
    """
    Script command switch case.

    Args:
        options (dict[str, str]): CLI options
    """

    command_name = next(command for command in _COMMAND_OPTIONS.keys() if options[command])
    return _COMMAND_OPTIONS[command_name](options)

def _get_cmd_doc(command_name: str) -> str:
    """
    Return the doc of the given command name.

    Args:
        command_name (str): The name of the command to retrieve the doc of

    Returns:
        type and description of the returned object.
    """

    return _COMMAND_OPTIONS[command_name].__doc__ or ""

def _build_doc(cmd_name: str) -> str:
    """
    Build docopt doc.

    Returns:
        str: Final documentation
    """

    full_doc = _BASE_DOC

    full_doc += "Commands:\n"
    for k in _COMMAND_OPTIONS:
        full_doc += f"  {k}\n"

    if cmd_name in _COMMAND_OPTIONS and cmd_name != "--help":
        full_doc += "\n".join(_get_cmd_doc(cmd_name).split("\n")[2:])

    full_doc += _OPT_DOC
    full_doc += _HELP_DOC

    return full_doc

def main() -> None:
    """
    Program entry point that runs each time the 'oudjat' command line is executed.
    """

    try:
        start_time = datetime.now().timestamp()
        options = docopt(_build_doc(sys.argv[1]), version=VERSION)

        original_stdout = sys.stdout

        logger = _config_logging(options)

        if options["--output"] and options["--silent"]:
            sys.stdout = StdOutHook(options["FILENAME"], options["--silent"], options["--output"])

        if not options["--target"] and not options["--file"] and not options["--directory"]:
            logger.error("Target required! Use -h to see usage. Either -f or -t")
            return

        if options["--target"] and options["--file"]:
            logger.error("Please only supply one target method - either -f or -t.")
            return

        ColorPrint.blue(banner)

        logger.info(f"{Context()}::Oudjat starts -  {datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S")} ")

        command = _command_switch(options)
        command.run()

        logger.info(f"Oudjat runtime -  {TimeConverter.seconds_to_str(datetime.now().timestamp() - start_time)}s")

        sys.stdout = original_stdout

    except KeyboardInterrupt:
        print("\nQuitting...")
        sys.exit(0)
