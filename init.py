#!/usr/bin/env python3

# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## Script to set configurations & launch Debreate.
#
#  Checks if the config file exists ~/.config/debreate.conf.
#  If not, a new one will be created.
#
#  @script init.py

import errno
import os
import sys
import traceback

# include libdbr in module search path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib"))


def main():
  import globals.paths
  import util

  from dbr.language  import setTranslator
  from libdbr        import compat
  from libdbr        import paths
  from libdbr        import sysinfo
  from libdbr.logger import Logger
  from libdebreate   import appinfo
  from startup       import command_line
  from startup       import wxprompt


  # module name displayed for logger output.
  script_name = os.path.basename(os.path.realpath(__file__))

  logger = Logger(script_name)
  logger.startLogging(globals.paths.getLogsDir())

  # check for compatible Python version
  err, msg = compat.checkPython((3, 10))
  if err != 0:
    logger.error(msg)
    logger.endLogging()
    sys.exit(err)

  # initialize command line parser
  command_line.init(os.path.basename(sys.argv[0]))

  logger.setLevel(command_line.options.log_level)

  dir_app = paths.getAppDir()

  setTranslator(appinfo.getLocaleDir())

  # Compiles python source into bytecode
  if command_line.options.command == "compile":
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

  if command_line.options.command == "clean":
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

  logger.info("system name: {}".format(sysinfo.getOSName()))

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

  from ui.app import DebreateApp

  # initialize app before importing local modules
  debreate_app = DebreateApp()

  import dbr.config
  import ui.main

  from dbr.config          import ConfCode
  from dbr.config          import GetDefaultConfigValue
  from dbr.language        import GetLocaleDir
  from dbr.language        import GT
  from dbr.workingdir      import ChangeWorkingDirectory
  from globals.strings     import GS
  from globals.system      import PY_VER_STRING
  from globals.system      import WX_VER_STRING
  from startup             import firstrun
  from system              import display
  from startup             import startup


  if ".py" in script_name:
    script_name = script_name.split(".py")[0]

  logger.info("Python version: {}".format(PY_VER_STRING))
  logger.info("wxPython version: {}".format(WX_VER_STRING))
  logger.info("Debreate version: {}".format(appinfo.getVersionString()))
  logger.info("logging level: {}".format(logger.getLevelString()))

  first_run = startup.initConfig()

  debreate_app.setMainWindow(ui.main.MainWindow())
  Debreate = debreate_app.getMainWindow()

  conf_values = dbr.config.getConfiguration()

  working_dir = conf_values["workingdir"]
  Debreate.SetSize(wx.Size(conf_values["size"][0], conf_values["size"][1]))
  Debreate.SetPosition(wx.Point(conf_values["position"][0], conf_values["position"][1]))
  if conf_values["maximize"]:
    Debreate.Maximize()
  elif conf_values["center"]:
    display.centerOnPrimary(Debreate)

  def logger_callback():
    logger.debug("shutting down app from logger")
    Debreate.saveConfigAndShutdown()
  logger.setCallback(logger_callback)

  Debreate.InitWizard()
  if command_line.options.project:
    logger.debug(GT("Opening project from argument: {}").format(command_line.options.project))
    if Debreate.OpenProject(command_line.options.project):
      working_dir = os.path.dirname(command_line.options.project)

  # Set working directory
  ChangeWorkingDirectory(working_dir)

  Debreate.Show(True)
  if first_run:
    firstrun.launch()

  # Wait for window to be constructed (prevents being marked as dirty project after initialization)
  # ~ wx.GetApp().Yield()

  # Set initialization state to 'True'
  # ~ SetAppInitialized()

  debreate_app.MainLoop()

  logger.endLogging()


if __name__ == "__main__":
  try:
    main()
  except Exception:
    msg = "An unhandled exception occurred and Debreate shut down:\n{}" \
        .format(traceback.format_exc())
    sys.stderr.write("{}\n".format(msg))
    if "wx" not in sys.modules:
      try:
        import wx
      except:
        pass
    if "wx" in sys.modules:
      wx = sys.modules["wx"]
      debreate_app = wx.GetApp()
      if debreate_app:
        debreate_app.shutdown()
      # create a new app to show error dialog
      app = wx.App()
      # FIXME: show error in current locale
      dia = wx.MessageDialog(None, msg, "Error", style=wx.ICON_ERROR)
      app.SetTopWindow(dia)
      dia.ShowModal()
      dia.Destroy()
else:
  raise RuntimeWarning("Debreate cannot be imported as a module")
