
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module command_line

import argparse
import sys

from globals.application import VERSION_string
from libdbr              import clformat
from libdbr.logger       import LogLevel
from libdbr.logger       import Logger
from libdbr.strings      import sgr
from startup.tests       import available_tests
from startup.tests       import test_list


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

  parser = argparse.ArgumentParser(
    prog = exe,
    formatter_class = clformat.Formatter,
    add_help = False,
    allow_abbrev = False
  )
  parser.version = VERSION_string

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
  parser.add_argument("-t", "--test", metavar="<test>", choices=("update-fail", "alpha"),
      help=sgr("Run supplied tests during execution for debugging."
          + "\n  <bold>update-fail</bold>\n  <bold>alpha</bold>"))
  parser.add_argument("project", nargs="?", default=None, help="Project file to load.")
  options = parser.parse_args()

  err = LogLevel.check(options.log_level)
  if isinstance(err, Exception):
    __logger.error(err)
    parser.print_help()
    exit(1)


## Solo args
#
#  -h or --help
#  Display usage information in the command line.
#  -v or --version
#  Display Debreate version in the command line & exit
solo_args = (
  ("h", "help"),
  ("v", "version"),
)

## Value args
#
#  -l or --log-level
#  Sets logging output level. Values can be 'quiet', 'info', 'warn', 'error', or debug,
#  or equivalent numeric values of 0-4. Default is 'error' (3).
#  -i or --log-interval
#  Set the refresh interval, in seconds, for updating the log window.
value_args = (
  ("l", "log-level"),
  ("i", "log-interval"),
)

cmds = (
  "clean",
  "compile",
  "test",
)

parsed_args_s = []
parsed_args_v = {}
parsed_commands = []
parsed_path = None


def ArgOK(arg, group):
  __logger.deprecated(ArgOK)

  for s, l in group:
    if arg in (s, l,):
      return True

  return False


def ArgIsDefined(arg, a_type):
  __logger.deprecated(ArgIsDefined)

  for group in (solo_args, value_args):
    for SET in group:
      for A in SET:
        if arg == A:
          return True

  return False


def GetArgType(arg):
  __logger.deprecated(GetArgType)

  dashes = 0
  for C in arg:
    if C != "-":
      break

    dashes += 1

  if dashes:
    if dashes == 2 and len(arg.split("=")[0]) > 2:
      if not arg.count("="):
        return "long"

      if arg.count("=") == 1:
        return "long-value"

    elif dashes == 1 and len(arg.split("=")[0]) == 2:
      if not arg.count("="):
        return "short"

      if arg.count("=") == 1:
        return "short-value"

    return None

  if arg in cmds:
    return "command"

  # Any other arguments should be a filename path
  return "path"


def ParseArguments(arg_list):
  __logger.deprecated(ParseArguments)

  global parsed_path, parsed_commands, parsed_args_s, parsed_args_v

  if "test" in arg_list:
    testcmd_index = arg_list.index("test")
    tests = arg_list[testcmd_index+1:]

    if not tests:
      print("ERROR: Must supply at least one test")
      sys.exit(1)

    for TEST in tests:
      if TEST not in available_tests:
        print("ERROR: Unrecognized test: {}".format(TEST))
        sys.exit(1)

      test_list.append(TEST)

      # Remove tests from arguments
      arg_list.pop(testcmd_index + 1)

    # Remove test command from arguments
    arg_list.pop(testcmd_index)

  argc = len(arg_list)

  for AINDEX in range(argc):
    if AINDEX >= argc:
      break

    A = arg_list[AINDEX]
    arg_type = GetArgType(A)

    if arg_type == None:
      print("ERROR: Malformed argument: {}".format(A))
      sys.exit(1)

    if arg_type == "command":
      parsed_commands.append(A)
      continue

    if arg_type == "path":
      if parsed_path != None:
        print("ERROR: Extra input file detected: {}".format(A))
        # FIXME: Use errno here
        sys.exit(1)

      parsed_path = A
      continue

    clip = 0
    for C in A:
      if C != "-":
        break

      clip += 1

    if arg_type in ("long", "short"):
      parsed_args_s.append(A[clip:])
      continue

    # Anything else should be a value type
    key, value = A.split("=")

    # FIXME: Value args can be declared multiple times

    if not value.strip():
      print("ERROR: Value argument with empty value: {}".format(key))
      # FIXME: Use errno here
      sys.exit(1)

    key = key[clip:]

    # Use long form
    for S, L in value_args:
      if key == S:
        key = L
        break

    # Allow using 'warning' as 'alias' for 'log-level'
    if key == "log-level" and value == "warning":
      value = "warn"

    parsed_args_v[key] = value

  for A in parsed_args_s:
    if not ArgOK(A, solo_args):
      for S, L in value_args:
        if A in (S, L,):
          print("ERROR: Value argument with empty value: {}".format(A))
          # FIXME: Use errno here:
          sys.exit(1)

      print("ERROR: Unknown argument: {}".format(A))
      # FIXME: Use errno here
      sys.exit(1)

    # Use long form
    arg_index = parsed_args_s.index(A)
    for S, L in solo_args:
      if A == S:
        parsed_args_s[arg_index] = L

  for A in parsed_args_v:
    if not ArgOK(A, value_args):
      print("ERROR: Unknown argument: {}".format(A))
      # FIXME: Use errno here
      sys.exit(1)

  for S, L in solo_args:
    s_count = parsed_args_s.count(S)
    l_count = parsed_args_s.count(L)

    if s_count + l_count > 1:
      print("ERROR: Duplicate arguments: -{}|--{}".format(S, L))
      # FIXME: Use errno here
      sys.exit(1)


## Checks if an argument was used
def FoundArg(arg):
  __logger.deprecated(FoundArg)

  for group in (parsed_args_s, parsed_args_v):
    for A in group:
      if A == arg:
        return True

  return False


## Checks if a command was used
def FoundCmd(cmd):
  __logger.deprecated(FoundCmd)

  return cmd in parsed_commands


def GetParsedPath():
  __logger.deprecated(GetParsedPath)

  return parsed_path
