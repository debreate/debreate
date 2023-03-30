#!/usr/bin/env python3

## \page init.py Initialization Script
#  Script to set configurations and launch Debreate
#
#  Checks if the config file exists in ~/.config/debreate. If
#  not, a new file will be created (~/.config/debreate/config).
#  If the config file already exists but is corrupted, it will
#  reset it to its default settings.


import errno, os, sys

import util

from command_line  import GetParsedPath
from command_line  import ParseArguments
from command_line  import parsed_commands
from command_line  import parsed_args_s
from command_line  import parsed_args_v
from globals.paths import PATH_app
from globals.paths import ConcatPaths

logger = util.getLogger()
logger.startLogging()

## Module name displayed for Logger output.
#  Should be set to 'init' or actual name of executable script.
script_name = os.path.basename(__file__)

# *** Command line arguments
ParseArguments(sys.argv[1:])

# GetParsedPath must be called after ParseArguments
parsed_path = GetParsedPath()


# Compiles python source into bytecode
if "compile" in parsed_commands:
  import compileall


  compile_dirs = (
    "dbr",
    "globals",
    "wizbin",
    )

  if not os.access(PATH_app, os.W_OK):
    print("ERROR: No write privileges for {}".format(PATH_app))
    sys.exit(errno.EACCES)

  print("Compiling Python modules (.py) to bytecode (.pyc) ...\n")

  print("Compiling root directory: {}".format(PATH_app))
  for F in os.listdir(PATH_app):
    if os.path.isfile(F) and F.endswith(".py") and F != "init.py":
      F = ConcatPaths((PATH_app, F))
      compileall.compile_file(F)

  print

  for D in os.listdir(PATH_app):
    D = ConcatPaths((PATH_app, D))
    if os.path.isdir(D) and os.path.basename(D) in compile_dirs:
      print("Compiling directory: {}".format(D))
      compileall.compile_dir(D)
      print

  sys.exit(0)


if "clean" in parsed_commands:
  if not os.access(PATH_app, os.W_OK):
    print("ERROR: No write privileges for {}".format(PATH_app))
    sys.exit(errno.EACCES)

  print("Cleaning Python bytecode (.pyc) ...\n")

  for ROOT, DIRS, FILES in os.walk(PATH_app):
    for F in FILES:
      F = ConcatPaths((ROOT, F))

      if os.path.isfile(F) and F.endswith(".pyc"):
        print("Removing file: {}".format(F))
        os.remove(F)

  sys.exit(0)


import subprocess, gettext, wx


from dbr.app import DebreateApp

# Initialize app before importing local modules
debreate_app = DebreateApp()

from dbr.config          import ConfCode
from dbr.config          import GetAllConfigKeys
from dbr.config          import GetDefaultConfigValue
from dbr.language        import GetLocaleDir
from dbr.language        import GT
from dbr.language        import SetLocaleDir
from dbr.language        import TRANSLATION_DOMAIN
from dbr.log             import Logger
from dbr.workingdir      import ChangeWorkingDirectory
from globals.application import VERSION_string
from globals.constants   import INSTALLED
from globals.constants   import PREFIX
from globals.strings     import GS
from globals.system      import PY_VER_STRING
from globals.system      import WX_VER_STRING
from main                import MainWindow
from startup.firstrun    import LaunchFirstRun
from startup.startup     import SetAppInitialized


# FIXME: How to check if text domain is set correctly?
if INSTALLED:
  SetLocaleDir(ConcatPaths((PREFIX, "share/locale")))
  gettext.install(TRANSLATION_DOMAIN, GetLocaleDir())


if ".py" in script_name:
  script_name = script_name.split(".py")[0]

exit_now = 0

if "version" in parsed_args_s:
  print(VERSION_string)

  sys.exit(0)


if "help" in parsed_args_s:
  if INSTALLED:
    res = subprocess.run(["man", "debreate"])

  else:
    res = subprocess.run(["man", "--manpath=\"{}/man\"".format(PATH_app), "debreate"])

  help_output = (res.returncode, res.stdout)


  if help_output[0]:
    print("ERROR: Could not locate manpage")

    sys.exit(help_output[0])


  help_output = GS(help_output[1])
  print("\n".join(help_output.split("\n")[2:-1]))

  sys.exit(0)


if "log-level" in parsed_args_v:
  Logger.SetLogLevel(parsed_args_v["log-level"])


Logger.Info(script_name, "Python version: {}".format(PY_VER_STRING))
Logger.Info(script_name, "wx.Python version: {}".format(WX_VER_STRING))
Logger.Info(script_name, "Debreate version: {}".format(VERSION_string))
Logger.Info(script_name, "Logging level: {}".format(Logger.GetLogLevel()))

# Check for & parse existing configuration
conf_values = GetAllConfigKeys()

if not conf_values:
  Logger.Debug(script_name, "Launching First Run dialog ...")

  first_run = LaunchFirstRun(debreate_app)
  if not first_run == ConfCode.SUCCESS:

    sys.exit(first_run)

  conf_values = GetAllConfigKeys()

# Check that all configuration values are okay
for V in conf_values:
  key = V
  value = conf_values[V]

  # ???: Redundant???
  if value == None:
    value = GetDefaultConfigValue(key)

  Logger.Debug(script_name, GT("Configuration key \"{}\" = \"{}\", type: {}".format(key, GS(value), type(value))))

  # FIXME: ConfCode values are integers & could cause problems with config values
  if conf_values[V] in (ConfCode.FILE_NOT_FOUND, ConfCode.KEY_NOT_DEFINED, ConfCode.KEY_NO_EXIST,):
    first_run = LaunchFirstRun(debreate_app)
    if not first_run == ConfCode.SUCCESS:
      sys.exit(first_run)

    break


Debreate = MainWindow(conf_values["position"], conf_values["size"])
debreate_app.SetMainWindow(Debreate)
Debreate.InitWizard()

if conf_values["maximize"]:
  Debreate.Maximize()

elif conf_values["center"]:
  from system.display import CenterOnPrimaryDisplay

  # NOTE: May be a few pixels off
  CenterOnPrimaryDisplay(Debreate)

working_dir = conf_values["workingdir"]

if parsed_path:
  project_file = parsed_path
  Logger.Debug(script_name, GT("Opening project from argument: {}").format(project_file))

  if Debreate.OpenProject(project_file):
    working_dir = os.path.dirname(project_file)

# Set working directory
ChangeWorkingDirectory(working_dir)

Debreate.Show(True)

# Wait for window to be constructed (prevents being marked as dirty project after initialization)
wx.GetApp().Yield()

# Set initializaton state to 'True'
SetAppInitialized()

debreate_app.MainLoop()

logger.endLogging()

sys.exit(0)
