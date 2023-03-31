## \package dbr.log

# MIT licensing
# See: docs/LICENSE.txt


import os, sys

import util

from globals import paths
from globals.fileio   import AppendFile
from globals.strings  import GetModuleString
from globals.strings  import IsString
from util.logger      import LogLevel

logger = util.getLogger()

# backward compat
LogLevel.TEST = LogLevel.DEBUG + 1

## A log class for outputting messages
#
#  TODO: delete
#
#  @deprecated
#    Use util.logger.
#
#  A log that will output messages to the terminal &
#  a log text file.
class DebreateLogger:
  LogLevelList = {
    LogLevel.INFO: "info",
    LogLevel.WARN: "warn",
    LogLevel.ERROR: "error",
    LogLevel.DEBUG: "debug",
    LogLevel.TEST: "test",
  }

  ## Constructor
  #
  #  \param level
  #  \b \e int|str : The level at which messages will be output (default is 2 (ERROR))
  #  \param logsPath
  #  \b \e str : The file to which messages will be written
  def __init__(self, level=LogLevel.ERROR, logsPath=paths.getLogsDir()):
    logger.deprecated(__name__, DebreateLogger.__name__, "util.logger.getLogger")

    ## The level at which to output messages
    self.LogLevel = level

    ## Directory where logs are located
    self.LogsDir = logsPath

    ## Log file path
    self.LogFile = logger.getLogFile()

    ## Forces space between header & first log entry (changed to None after first entry)
    self.NoStrip = "\n"

    self.OnInit()


  ## Opens a log file or creates a new one & adds log header with timestamp
  def OnInit(self):
    logger.deprecated(__name__, self.OnInit.__name__, "util.logger.Logger.startLogging")
    logger.startLogging()


  ## Adds footer with timestamp to log file
  def OnClose(self):
    logger.deprecated(__name__, self.OnClose.__name__, "util.logger.Logger.endLogging")
    logger.endLogging()


  ## Checks if log can be written at supplied level
  #
  #  \param level
  #  	\b \e int|str : The desired message level to output
  #  \return
  #  	\b \e tuple container int & str values of output level,
  #  	  or None for invalid log level
  def CheckLogLevel(self, level):
    logger.deprecated(__name__, self.CheckLogLevel.__name__)

    # Check if level is of type INFO, WARN, ERROR, DEBUG, TEST
    if level in self.LogLevelList:
      return level

    # Check if level is a string value of 'info', 'warn', 'error', 'debug', 'test'
    if isinstance(level, str):
      for L in self.LogLevelList:
        if level.lower() == self.LogLevelList[L].lower():
          return L

    return None


  ## Prints a message to stdout & logs to file
  #
  #  \param level
  #  Level at which to display the message
  #  \param module
  #  Name of the script/module or the globals.moduleaccess.ModuleAccessCtrl
  #  instance where the message originates
  #  \param message
  #  Message to display
  #  \param newline
  #  If <b><i>True</i></b>, prepends an empty line to beginning of message
  #  \param pout
  #  Stream to which message should be output (stdout/stderr)
  def LogMessage(self, level, module, message, details=[], newline=False, pout=sys.stdout):
    logger.deprecated(__name__, self.LogMessage.__name__, "util.logger.Logger.log")

    level = self.CheckLogLevel(level)

    # Use the object to retrieve module string
    if not IsString(module):
      module = GetModuleString(module)

    if (level in self.LogLevelList) and (level <= self.LogLevel):
      l_string = self.LogLevelList[level].upper()
      message = "{}: [{}] {}".format(l_string, module, message)

      if details:
        if IsString(details):
          message += "\n  • {}".format(details)

        else:
          for ITEM in details:
            message += "\n  • {}".format(ITEM)

      if newline:
        message = "\n{}".format(message)

      # Message is shown in terminal
      if pout not in (sys.stdout, sys.stderr,):
        print(message)

      else:
        # Need to manually add newline when using sys.stdout/sys.stderr
        pout.write("{}\n".format(message))

      # Open log for writing
      AppendFile(self.LogFile, "{}\n".format(message), self.NoStrip)

      # Allow stripping leading & trailing newlines from opened log file
      if self.NoStrip:
        self.NoStrip = None


  ## Show a log message at 'info' level
  #
  #  \param module
  #  Name of the script/module where the message originates
  #  \param message
  #  Message to display
  #  \param newline
  #  If <b><i>True</i></b>, prepends an empty line to beginning of message
  def Info(self, module, message, details=[], newline=False):
    logger.deprecated(__name__, self.Info.__name__, "util.logger.Logger.info")

    self.LogMessage("info", module, message, details=details, newline=newline)


  ## Show a log message at 'warn' level
  #
  #  \param module
  #  Name of the script/module where the message originates
  #  \param message
  #  Message to display
  #  \param newline
  #  If <b><i>True</i></b>, prepends an empty line to beginning of message
  def Warn(self, module, message, details=[], newline=False):
    logger.deprecated(__name__, self.Warn.__name__, "util.logger.Logger.warn")

    self.LogMessage("warn", module, message, details=details, newline=newline)


  ## Show a log message at 'error' level
  #
  #  Messages at 'error' level are written to stderr
  #
  #  \param module
  #  Name of the script/module where the message originates
  #  \param message
  #  Message to display
  #  \param newline
  #  If <b><i>True</i></b>, prepends an empty line to beginning of message
  def Error(self, module, message, details=[], newline=False):
    logger.deprecated(__name__, self.Error.__name__, "util.logger.Logger.error")

    self.LogMessage("error", module, message, details=details, newline=newline, pout=sys.stderr)


  ## Show a log message at 'debug' level
  #
  #  \param module
  #  Name of the script/module where the message originates
  #  \param message
  #  Message to display
  #  \param newline
  #  If <b><i>True</i></b>, prepends an empty line to beginning of message
  def Debug(self, module, message, details=[], newline=False):
    logger.deprecated(__name__, self.Debug.__name__, "util.logger.Logger.debug")

    self.LogMessage("debug", module, message, details=details, newline=newline)


  ## Show a log message at '' level
  #
  #  \param module
  #  Name of the script/module where the message originates
  #  \param message
  #  Message to display
  #  \param newline
  #  If <b><i>True</i></b>, prepends an empty line to beginning of message
  def Test(self, module, message, details=[], newline=False):
    logger.deprecated(__name__, self.Test.__name__)

    self.LogMessage("test", module, message, details=details, newline=newline)


  ## Sets the level at which messages will be output to terminal & log file
  #
  #  \param level
  #  	Level at which to print & output messages
  #  \return
  #  <b><i>True</i></b> if log level successfully set
  def SetLogLevel(self, level):
    logger.deprecated(__name__, self.SetLogLevel.__name__, "util.logger.Logger.setLevel")

    log_set = False

    if level.isdigit():
      level = int(level)

    if level in self.LogLevelList:
      self.LogLevel = level
      log_set = True

    elif isinstance(level, str):
      for L in self.LogLevelList:
        if level.lower() == self.LogLevelList[L].lower():
          self.LogLevel = L
          log_set = True

    return log_set


  ## Retrieves the current logging level
  #
  #  \return
  #  <b><i>Integer</i></b> logging level
  def GetLogLevel(self):
    logger.deprecated(__name__, self.GetLogLevel.__name__, "util.logger.Logger.getLevel")

    return self.LogLevel


  ## Retrieves the current file be written to
  #
  #  \return
  #  <b><i>String</i></b> path of log file
  def GetLogFile(self):
    logger.deprecated(__name__, self.GetLogFile.__name__)

    return self.LogFile


## Instantiated logger with default level & output path
Logger = DebreateLogger()

## Checks if logging level is set to 'debug'
#
#  \return
#  <b><i>True</i></b> if logging level is 'debug'
def DebugEnabled():
  logger.deprecated(__name__, DebugEnabled.__name__)

  return Logger.GetLogLevel() >= LogLevel.DEBUG
