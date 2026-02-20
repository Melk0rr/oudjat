"""
Oudjat main entry point.
"""

import logging
import sys
from datetime import datetime
from typing import Any

from docopt import docopt

from oudjat.banner import banner
from oudjat.commands import (
    EOLConnectorCommand,
    S1ConnectorCommand,
)
from oudjat.utils import ColorPrint, Context, StdOutHook, TimeConverter
from oudjat.utils.doc_builder import DocBuilder, DocCommand, DocOption
from oudjat.utils.logging import oudjatLogger

from . import __version__ as VERSION

_COMMAND_OPTIONS = {
    "connectors.edr.sentinelone": S1ConnectorCommand,
    "connectors.endoflife": EOLConnectorCommand,
}


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


def _base_doc() -> "DocBuilder":
    """
    Return the base doc builder.

    Returns:
        DocBuilder: A doc builder instance containing the base program options and usages
    """

    description = """
Oudjat is a SOC toolbox that provides an entry point to various data sources.
It also allows for complex data consolidation and mapping through a config file system.

** The following doc string is dynamically generated based on the command you chose **"""

    builder = DocBuilder("oudjat", description)

    # builder.commands = {
    #     cmd.__cmd_props__.name: DocCommand(cmd.__cmd_props__.name, cmd.__cmd_props__.description)
    #     for cmd in _COMMAND_OPTIONS.values()
    # }

    builder.usages = [
        "-h | --help",
        "-V | --version",
    ]

    builder.add_option("append", "Append to the output fileappend to the output file", short="a")
    builder.add_option("help", "Print the doc string", short="h")
    builder.add_option("log", "Specify the logging level", arg="LOGGING", short="l", default="INFO")
    builder.add_option("output", "Specify a file to save the execution logs to", arg="LOGFILE", short="o")
    builder.add_option("silent", "Simple output", short="S")
    builder.add_option("version", "Show the program version and exit", short="V")
    builder.add_option("csv", "Save results as a CSV file", arg="CSV")
    builder.add_option("json", "Save results as a JSON file", arg="JSON")

    builder.help_content = [
        "For help using this tool, please open an issue on the Codeberg repository:",
        "https://codeberg.org/me1k0r/oudjat",
    ]

    return builder


def _build_doc(cmd_name: str) -> "DocBuilder":
    """
    Return the final doc builder to be converted as a string and passed to docopt.

    Returns:
        DocBuilder: Final doc builder based on base doc and merged with the chosen command builder
    """

    doc = _base_doc()
    cmd_builder = _COMMAND_OPTIONS[cmd_name].__doc_builder__

    doc.merge(cmd_builder)

    return doc


def main() -> None:
    """
    Program entry point that runs each time the 'oudjat' command line is executed.
    """

    try:
        start_time = datetime.now().timestamp()

        __doc__ = _build_doc(sys.argv[1])
        options = docopt(str(__doc__), version=VERSION)

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

        logger.info(
            f"{Context()}::Oudjat starts -  {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')} "
        )

        command = _command_switch(options)
        command.run()

        logger.info(
            f"Oudjat runtime -  {TimeConverter.seconds_to_str(datetime.now().timestamp() - start_time)}s"
        )

        sys.stdout = original_stdout

    except KeyboardInterrupt:
        print("\nQuitting...")
        sys.exit(0)
