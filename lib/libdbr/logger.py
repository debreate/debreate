
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## Message logging.
#
#  @module libdbr.logger

import errno
import os
import sys
import types

from .         import dateinfo
from .         import fileio
from .dateinfo import dtfmt

## Exception class for log level errors.
#
#  @param msg
#    Optional text to display with error.
class LogLevelError(Exception):
  def __init__(self, msg=None):
    super().__init__(msg)

## Logging level enumeration.
class LogLevel:
  ## Integer representations of logging levels.
  __levels = range(0, 5)
  SILENT, ERROR, WARN, INFO, DEBUG = __levels

  ## String representations of logging levels.
  __level_names = ()
  ## Default logging level.
  __default = INFO

  ## Checks for a valid level representation.
  #
  #  @param level
  #    Passed value to be checked.
  #  @return
  #    Error or None.
  @staticmethod
  def check(level):
    try:
      # allow string integer representations
      level = int(level)
    except ValueError:
      pass
    l_type = type(level)
    if l_type == int:
      if level not in LogLevel.__levels:
        return LogLevelError("level must be within range '{}-{}', found '{}'".format(
            LogLevel.__levels[0], LogLevel.__levels[-1], level))
      return level
    if l_type == str:
      v_up = level.upper()
      l_names = LogLevel.getLevelsNames()
      if v_up not in l_names:
        return LogLevelError("level must be one of '{}', found '{}'".format("|".join(l_names), level))
      return v_up
    return LogLevelError("level type must be 'int' or 'str', found '{}'".format(l_type))

  ## Retrivies default logging level.
  #
  #  @return
  #    Default log level.
  @staticmethod
  def getDefault():
    return LogLevel.__default

  ## Sets default logging level.
  #
  #  @param level
  #    Logging level.
  @staticmethod
  def setDefault(level):
    level = LogLevel.check(level)
    if isinstance(level, Exception):
      raise level

    if type(level) == str:
      level = LogLevel.fromString(level)
    LogLevel.__default = level

  ## Converts logging level to string representation.
  #
  #  @param level
  #    Logging level.
  #  @return
  #    Logging level string representation.
  @staticmethod
  def toString(level):
    level = LogLevel.check(level)
    if isinstance(level, Exception):
      raise level

    for lname in LogLevel.getLevelsNames():
      if level == getattr(LogLevel, lname):
        return lname
    return LogLevel.toString(LogLevel.getDefault())

  ## Converts logging level from string representation.
  #
  #  @param level
  #    Logging level string representation.
  #  @return
  #    Logging level.
  @staticmethod
  def fromString(level):
    level = LogLevel.check(level)
    if isinstance(level, Exception):
      raise level

    if type(level) == str and hasattr(LogLevel, level):
      return getattr(LogLevel, level)
    return level

  ## Retrieves available logging levels.
  #
  #  @return
  #    List of logging levels.
  @staticmethod
  def getLevels():
    return tuple(LogLevel.__levels)

  ## Retrieves available logging levels.
  #
  #  @return
  #    List of logging levels string representations.
  @staticmethod
  def getLevelsNames():
    if LogLevel.__level_names:
      return LogLevel.__level_names
    lnames = []
    for attr in vars(LogLevel):
      if attr.startswith("_") or type(getattr(LogLevel, attr)) != int:
        continue
      lnames.append(attr)
    LogLevel.__level_names = tuple(lnames)
    return LogLevel.__level_names

## Class for logging messages to stdout/stdin & file.
#
#  TODO:
#    - add timestamps
class Logger:
  initialized = False
  loglevel = LogLevel.getDefault()
  logfile = None
  logsdir = None
  callback: types.FunctionType = None

  def __init__(self, _id=None):
    self.id = _id

  ## Initializes logging & adds header to log file.
  #
  #  @param logsdir
  #    Path to directory where log files are to be stored.
  #  @param callback
  #    Action to notify the main app to shutdown.
  @staticmethod
  def startLogging(logsdir=None, callback: types.FunctionType=None):
    if Logger.initialized:
      Logger.warn(Logger, "tried to re-inizialize logging")
      return
    Logger.initialized = True
    Logger.logsdir = os.path.normpath(logsdir) if logsdir != None else logsdir
    Logger.callback = callback

    if not os.path.isdir(Logger.logsdir):
      if os.path.exists(Logger.logsdir):
        Logger.error(Logger,
            "cannot create logs directory, file exists: {}".format(Logger.logsdir))
        sys.exit(errno.EEXIST)
      os.makedirs(Logger.logsdir)
    date_start = dateinfo.getDate(dtfmt.LOG)
    time_start = dateinfo.getTime(dtfmt.LOG)
    Logger.logfile = os.path.join(Logger.logsdir, date_start + ".txt")

    date_time = "{} {}".format(date_start, time_start)
    header = "--------------- Log Start: {} ---------------\n".format(date_time)
    # write header to log file
    fileio.appendFile(Logger.logfile, header)

  ## Appends footer to log file.
  @staticmethod
  def endLogging():
    if not Logger.logfile or not os.path.isfile(Logger.logfile):
      # initialization failed or user deleted log file
      return
    date_time = "{} {}".format(dateinfo.getDate(dtfmt.LOG), dateinfo.getTime(dtfmt.LOG))
    footer = "\n--------------- Log End:   {} ---------------\n\n".format(date_time)
    fileio.appendFile(Logger.logfile, footer)
    Logger.logfile = None

  ## Ends logging & shuts down app.
  #
  #  @param ret
  #    Exit code.
  @staticmethod
  def shutdown(ret=0):
    Logger.endLogging()
    if type(Logger.callback) == types.FunctionType:
      Logger.callback() # pylint: disable=not-callable

  ## Sets the callback action for when the app should shutdown.
  #
  #  @param callback
  #    Action to notify the main app to shutdown.
  @staticmethod
  def setCallback(callback):
    Logger.callback = callback

  ## Sets verbosity of logger output.
  #
  #  @param level
  #    Verbosity level.
  @staticmethod
  def setLevel(loglevel):
    Logger.loglevel = LogLevel.fromString(loglevel)

  ## Retrieves level of verbosity.
  #
  #  @return
  #    Verbosity.
  @staticmethod
  def getLevel():
    return Logger.loglevel

  ## Retrieves level of verbosity.
  #
  #  @return
  #    Verbosity string representation.
  @staticmethod
  def getLevelString():
    return LogLevel.toString(Logger.loglevel)

  ## Retrieves log file.
  #
  #  @return
  #    Path to log file.
  @staticmethod
  def getLogFile():
    return Logger.logfile

  ## Checks if debugging is enabled.
  #
  #  @return
  #  True if logging level is >= LogLevel.DEBUG.
  @staticmethod
  def debugging():
    return Logger.getLevel() >= LogLevel.DEBUG

  ## Logs a message.
  #
  #  @param lvl
  #    Logging level at which the message is logged.
  #  @param msg
  #    Text of message to log.
  #  @param details
  #    Extra details to append to message.
  #  @param newline
  #    If true, appends a newline to end of message.
  def log(self, lvl, msg="", details=None, newline=False):
    if not msg:
      msg = lvl
      lvl = LogLevel.INFO
    if Logger.loglevel == LogLevel.SILENT or Logger.loglevel < lvl:
      return
    stream = sys.stdout
    if lvl == LogLevel.ERROR:
      stream = sys.stderr
    prefix = (LogLevel.toString(lvl) + ":")
    if self.id:
      prefix += " (" + self.id + ")"
    if isinstance(msg, Exception):
      msg = str(msg)
    msg = prefix.ljust(30) + " | " + msg
    if details:
      if type(details) == str:
        msg += "\n  • {}".format(details)
      else:
        for line in details:
          msg += "\n  • {}".format(line)
    if newline:
      msg = "\n" + msg
    stream.write(msg + "\n")
    # output to log file
    if Logger.logfile and os.path.isfile(Logger.logfile):
      fileio.appendFile(Logger.logfile, msg)

  ## Logs a message at debug level.
  #
  #  @param msg
  #    Text of message to log.
  #  @param details
  #    Extra details to append to message.
  #  @param newline
  #    If true, appends a newline to end of message.
  def debug(self, msg, details=None, newline=False):
    self.log(LogLevel.DEBUG, msg, details, newline)

  ## Logs a message at info level.
  #
  #  @param msg
  #    Text of message to log.
  #  @param details
  #    Extra details to append to message.
  #  @param newline
  #    If true, appends a newline to end of message.
  def info(self, msg, details=None, newline=False):
    self.log(LogLevel.INFO, msg, details, newline)

  ## Logs a message at warning level.
  #
  #  @param msg
  #    Text of message to log.
  #  @param details
  #    Extra details to append to message.
  #  @param newline
  #    If true, appends a newline to end of message.
  def warn(self, msg, details=None, newline=False):
    self.log(LogLevel.WARN, msg, details, newline)

  ## Logs a message at error level.
  #
  #  @param msg
  #    Text of message to log.
  #  @param details
  #    Extra details to append to message.
  #  @param newline
  #    If true, appends a newline to end of message.
  def error(self, msg, details=None, newline=False):
    self.log(LogLevel.ERROR, msg, details, newline)

  ## Logs a message denoting deprecation of an element.
  #
  #  @param obj
  #    Object or name of deprecated object.
  #  @param name
  #    Element name (deprecated).
  #  @param alt
  #    Information about alternatives.
  #  @param newline
  #    If true, appends a newline to end of message.
  def deprecated(self, obj, name=None, alt=None, newline=False):
    if name != None:
      self.deprecated("Logger.deprecated(obj, name)", alt="Logger.deprecated(obj)")

    alt_st = alt
    if alt != None and type(alt) != str:
      alt_st = alt.__module__ if hasattr(alt, "__module__") else ""
      if hasattr(alt, "__self__") and hasattr(alt.__self__, "__class__"):
        alt_st += "." + alt.__self__.__class__.__name__
      alt_st += "." + (alt.__name__ if hasattr(alt, "__name__") else str(alt))

    obj_st = obj
    if type(obj) != str:
      obj_st = obj.__module__ if hasattr(obj, "__module__") else ""
      if hasattr(obj, "__self__") and hasattr(obj.__self__, "__class__"):
        obj_st += "." + obj.__self__.__class__.__name__
      obj_st += "." + (obj.__name__ if hasattr(obj, "__name__") else str(obj))

    msg = obj_st
    if name != None:
      msg += "." + name
    msg += " is deprecated"
    if alt_st != None:
      msg += ", use " + alt_st + " instead"
    self.warn(msg, newline)
