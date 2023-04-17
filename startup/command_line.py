
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module startup.command_line

import argparse
import sys

from libdbr         import clformat
from libdbr.logger  import LogLevel
from libdbr.logger  import Logger
from libdbr.strings import sgr
from libdebreate    import appinfo
from startup        import tests


__logger = Logger(__name__)

## Options parsed from command line input.
options = {}

## Initializes command line parser.
def init(exe):
  global options
  if options:
    __logger.warn("tried to re-initialize command line input")
    return

  cmd_options = {
    "clean": "Remove compiled Python bytecode files (.pyc) from Debreate directory.",
    "compile": "Compile Debreate's source files (.py) into Python bytecode (.pyc)."
  }
  cmd_help = ["Execute a sub-command. Available commands are:"]
  for cmd_name in sorted(cmd_options):
    cmd_help.append(sgr("  <bold>{}:</bold> {}".format(cmd_name, cmd_options[cmd_name])))
  tests_help = []
  for t in tests.__available:
    tests_help.append(sgr("  <bold>{}:</bold> {}".format(t, tests.__available[t])))

  parser = argparse.ArgumentParser(
    prog = exe,
    formatter_class = clformat.Formatter,
    add_help = False,
    allow_abbrev = False
  )
  parser.version = appinfo.getVersionString()

  clformat.Formatter.description = "Debreate - Debian Package Builder"

  log_levels = []
  for level in LogLevel.getLevels():
    log_levels.append(sgr("<bold>{}) {}</bold>").format(level, LogLevel.toString(level).lower()))

  parser.add_argument("-h", "--help", action="help", help="Show this help summary.")
  parser.add_argument("-v", "--version", action="version", help="Show Debreate version.")
  parser.add_argument("-c", "--command", choices=tuple(cmd_options), metavar="<command>",
      help="\n".join(cmd_help))
  parser.add_argument("-l", "--log-level", metavar="<level>", #choices=LogLevel.strings, #, choices=("silent", "error", "warn", "info", "debug"),
      default=LogLevel.toString(LogLevel.getDefault()).lower(),
      help="Logging output verbosity.\n  " + "\n  ".join(log_levels))
  # ~ parser.add_argument("-i", "--log-interval", type=int, default=1, metavar="<interval>",
      # ~ help="Set the integer value refresh rate for the log window when debugging is enabled." \
          # ~ + " Higher value is lower frequency.")
  parser.add_argument("-t", "--test", metavar="<test>", #choices=("update-fail", "alpha"),
      help=sgr("Run supplied tests during execution for debugging. Can be a comma-separate list."
          + "\n" + "\n".join(tests_help)))
          # ~ + "\n  <bold>update-fail</bold>\n  <bold>alpha</bold>"))
  parser.add_argument("project", nargs="?", default=None, help="Project file to load.")
  options = parser.parse_args()

  err = LogLevel.check(options.log_level)
  if isinstance(err, Exception):
    sys.stderr.write(sgr("<red>ERROR: {}</fg>\n".format(err)))
    print()
    parser.print_help()
    exit(1)

  if options.test:
    for t in options.test.split(","):
      t = t.strip()
      if not t:
        continue
      try:
        tests.activate(t)
      except TypeError as err:
        sys.stderr.write(sgr("<red>ERROR: {}</fg>\n".format(err)))
        print()
        parser.print_help()
        exit(1)
