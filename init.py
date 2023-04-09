#!/usr/bin/env python3

## \page init.py Initialization Script
#  Script to set configurations and launch Debreate
#
#  Checks if the config file exists in ~/.config/debreate. If
#  not, a new file will be created (~/.config/debreate/config).
#  If the config file already exists but is corrupted, it will
#  reset it to its default settings.


import errno, os, sys

# include libdbr in module search path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib"))

import globals.paths
import util

from command_line  import GetParsedPath
from command_line  import ParseArguments
from command_line  import parsed_commands
from command_line  import parsed_args_s
from command_line  import parsed_args_v
from dbr.language  import setTranslator
from libdbr        import compat
from libdbr        import paths
from libdbr        import sysinfo
from libdbr.logger import Logger
from startup       import wxprompt


# module name displayed for logger output.
script_name = os.path.basename(os.path.realpath(__file__))

logger = Logger(script_name)
logger.startLogging(globals.paths.getLogsDir())

# check for compatible Python version
err, msg = compat.checkPython((3, 10))
if err != 0:
  logger.error(msg)
  sys.exit(err)

# *** Command line arguments
ParseArguments(sys.argv[1:])

# GetParsedPath must be called after ParseArguments
parsed_path = GetParsedPath()

dir_app = paths.getAppDir()

setTranslator(util.appinfo.getLocaleDir())

# Compiles python source into bytecode
if "compile" in parsed_commands:
  import compileall


  compile_dirs = (
    "dbr",
    "globals",
    "wizbin",
    )

  if not os.access(dir_app, os.W_OK):
    print("ERROR: No write privileges for {}".format(dir_app))
    sys.exit(errno.EACCES)

  print("Compiling Python modules (.py) to bytecode (.pyc) ...\n")

  print("Compiling root directory: {}".format(dir_app))
  for F in os.listdir(dir_app):
    if os.path.isfile(F) and F.endswith(".py") and F != "init.py":
      F = os.path.join(dir_app, F)
      compileall.compile_file(F)

  print

  for D in os.listdir(dir_app):
    D = os.path.join(dir_app, D)
    if os.path.isdir(D) and os.path.basename(D) in compile_dirs:
      print("Compiling directory: {}".format(D))
      compileall.compile_dir(D)
      print

  sys.exit(0)


if "clean" in parsed_commands:
  if not os.access(dir_app, os.W_OK):
    print("ERROR: No write privileges for {}".format(dir_app))
    sys.exit(errno.EACCES)

  print("Cleaning Python bytecode (.pyc) ...\n")

  for ROOT, DIRS, FILES in os.walk(dir_app):
    for F in FILES:
      F = os.path.join(ROOT, F)

      if os.path.isfile(F) and F.endswith(".pyc"):
        print("Removing file: {}".format(F))
        os.remove(F)

  sys.exit(0)

logger.info("operating system name: {}".format(sysinfo.getOSName()))

import subprocess, gettext

wx = util.getModule("wx")

if not wx:
  if sys.stdout.isatty():
    res = wxprompt.promptForWxInstall()
  else:
    cmd_args = [paths.join(paths.getAppDir(), "startup/wxprompt.py")]
    os_name = sysinfo.getOSName()
    t_param = None
    if os_name == "win32":
      # simply execute Python as console app
      t_exec = paths.getExecutable("python3") or paths.getExecutable("python")
      cmd_args.insert(0, t_exec)
    else:
      cmd_args.insert(0, sys.executable)
      t_exec, t_param = paths.getSystemTerminal()
      if not t_exec:
        logger.error("install wxPython to use Debreate ({} -m pip install wxPython)".format(sys.executable))
        sys.exit(errno.ENOENT)
      if t_param:
        cmd_args.insert(0, t_param)
      cmd_args.insert(0, t_exec)
    msg = "prompting for user input with terminal program: {}".format(t_exec)
    if t_param:
      msg += " " + t_param
    logger.info(msg)
    res = subprocess.run(cmd_args).returncode

  logger.debug("terminal execution result: {} ({})".format(res, type(res)))

  if res != 0:
    sys.exit(res)
  wx = util.getModule("wx")
  if not wx:
    logger.error("failed to install wxPython")
    sys.exit(errno.ENOENT)

util.checkWx()

from dbr.app import DebreateApp

# Initialize app before importing local modules
debreate_app = DebreateApp()

import dbr.config

from dbr.config          import ConfCode
# ~ from dbr.config          import GetAllConfigKeys
from dbr.config          import GetDefaultConfigValue
from dbr.language        import GetLocaleDir
from dbr.language        import GT
from dbr.workingdir      import ChangeWorkingDirectory
from globals.application import VERSION_string
from globals.strings     import GS
from globals.system      import PY_VER_STRING
from globals.system      import WX_VER_STRING
from startup.firstrun    import LaunchFirstRun
from startup.startup     import SetAppInitialized
from ui.main             import MainWindow


if ".py" in script_name:
  script_name = script_name.split(".py")[0]

exit_now = 0

if "version" in parsed_args_s:
  print(VERSION_string)

  sys.exit(0)


if "help" in parsed_args_s:
  if util.appinfo.isPortable():
    res = subprocess.run(["man", "--manpath=\"{}/man\"".format(dir_app), "debreate"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  else:
    res = subprocess.run(["man", "debreate"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if res.returncode != 0:
    print("ERROR: Could not locate manpage: {}".format(res.stderr.decode("utf-8")))
    sys.exit(res.returncode)
  print("\n".join(res.stdout.decode("utf-8").split("\n")[2:-1]))
  sys.exit(0)


if "log-level" in parsed_args_v:
  logger.setLevel(parsed_args_v["log-level"])


logger.info("Python version: {}".format(PY_VER_STRING))
logger.info("wx.Python version: {}".format(WX_VER_STRING))
logger.info("Debreate version: {}".format(VERSION_string))
logger.info("Logging level: {}".format(logger.getLevel()))

# Check for & parse existing configuration
# ~ conf_values = GetAllConfigKeys()
conf_values = dbr.config.getConfiguration()

if not conf_values:
  logger.debug("Launching First Run dialog ...")

  first_run = LaunchFirstRun(debreate_app)
  if not first_run == ConfCode.SUCCESS:

    sys.exit(first_run)

  # ~ conf_values = GetAllConfigKeys()
  conf_values = dbr.config.getConfiguration()

# Check that all configuration values are okay
for V in conf_values:
  key = V
  value = conf_values[V]

  # ???: Redundant???
  if value == None:
    value = GetDefaultConfigValue(key)

  logger.debug(GT("Configuration key \"{}\" = \"{}\", type: {}".format(key, GS(value), type(value))))

  # FIXME: ConfCode values are integers & could cause problems with config values
  if conf_values[V] in (ConfCode.FILE_NOT_FOUND, ConfCode.KEY_NOT_DEFINED, ConfCode.KEY_NO_EXIST,):
    first_run = LaunchFirstRun(debreate_app)
    if not first_run == ConfCode.SUCCESS:
      sys.exit(first_run)

    break


Debreate = MainWindow(conf_values["position"], conf_values["size"])
debreate_app.SetMainWindow(Debreate)
Debreate.InitWizard()

def logger_callback():
  logger.debug("shutting down app from logger")
  Debreate.saveConfigAndShutdown()

logger.setCallback(logger_callback)

if conf_values["maximize"]:
  Debreate.Maximize()

elif conf_values["center"]:
  from system.display import CenterOnPrimaryDisplay

  # NOTE: May be a few pixels off
  CenterOnPrimaryDisplay(Debreate)

working_dir = conf_values["workingdir"]

if parsed_path:
  project_file = parsed_path
  logger.debug(GT("Opening project from argument: {}").format(project_file))

  if Debreate.OpenProject(project_file):
    working_dir = os.path.dirname(project_file)

# Set working directory
ChangeWorkingDirectory(working_dir)

Debreate.Show(True)

# Wait for window to be constructed (prevents being marked as dirty project after initialization)
wx.GetApp().Yield()

# Set initialization state to 'True'
SetAppInitialized()

debreate_app.MainLoop()

logger.endLogging()
