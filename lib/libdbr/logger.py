
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

import errno
import os
import sys
import types

from libdbr          import dateinfo
from libdbr          import fileio
from libdbr.dateinfo import dtfmt


## Logging level enumeration.
class _LogLevel:
  SILENT, ERROR, WARN, INFO, DEBUG = range(0, 5)

  strings = {
    "": SILENT,
    "ERROR": ERROR,
    "WARN": WARN,
    "INFO": INFO,
    "DEBUG": DEBUG
  }

  @staticmethod
  def getDefault():
    return _LogLevel.INFO

  @staticmethod
  def toString(loglevel):
    for st in _LogLevel.strings:
      if _LogLevel.strings[st] == loglevel:
        if st == "WARN":
          st = "WARNING"
        return st
    return _LogLevel.getDefault()

  @staticmethod
  def fromString(st):
    return _LogLevel.strings[st] if st in _LogLevel.strings else _LogLevel.getDefault()

## Class for logging messages to stdout/stdin & file.
#
#  TODO:
#    - add timestamps
class _Logger:
  initialized = False
  loglevel = _LogLevel.INFO
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
    if _Logger.initialized:
      _Logger.warn(_Logger, "tried to re-inizialize logging")
      return
    _Logger.initialized = True
    _Logger.logsdir = os.path.normpath(logsdir) if logsdir != None else logsdir
    _Logger.callback = callback

    if not os.path.isdir(_Logger.logsdir):
      if os.path.exists(_Logger.logsdir):
        _Logger.error(_Logger,
            "cannot create logs directory, file exists: {}".format(_Logger.logsdir))
        sys.exit(errno.EEXIST)
      os.makedirs(_Logger.logsdir)
    date_start = dateinfo.getDate(dtfmt.LOG)
    time_start = dateinfo.getTime(dtfmt.LOG)
    _Logger.logfile = os.path.join(_Logger.logsdir, date_start + ".txt")

    date_time = "{} {}".format(date_start, time_start)
    header = "--------------- Log Start: {} ---------------\n".format(date_time)
    # write header to log file
    fileio.appendFile(_Logger.logfile, header)

  ## Appends footer to log file.
  @staticmethod
  def endLogging():
    if not _Logger.logfile or not os.path.isfile(_Logger.logfile):
      # initialization failed or user deleted log file
      return
    date_time = "{} {}".format(dateinfo.getDate(dtfmt.LOG), dateinfo.getTime(dtfmt.LOG))
    footer = "\n--------------- Log End:   {} ---------------\n\n".format(date_time)
    fileio.appendFile(_Logger.logfile, footer)
    _Logger.logfile = None

  ## Ends logging & shuts down app.
  #
  #  @param ret
  #    Exit code.
  @staticmethod
  def shutdown(ret=0):
    _Logger.endLogging()
    if type(_Logger.callback) == types.FunctionType:
      _Logger.callback() # pylint: disable=not-callable

  ## Sets the callback action for when the app should shutdown.
  #
  #  @param callback
  #    Action to notify the main app to shutdown.
  @staticmethod
  def setCallback(callback):
    _Logger.callback = callback

  ## Sets verbosity of logger output.
  #
  #  @param level
  #    Verbosity level.
  @staticmethod
  def setLevel(loglevel):
    if type(loglevel) == str:
      loglevel_up = loglevel.upper()
      if not loglevel_up in _LogLevel.strings:
        _Logger.warn(_Logger, "invalid logging level: " + loglevel)
      loglevel = _LogLevel.fromString(loglevel_up)
    _Logger.loglevel = loglevel

  ## Retrieves level of verbosity.
  #
  #  @return
  #    Verbosity.
  @staticmethod
  def getLevel():
    return _Logger.loglevel

  ## Retrieves log file.
  #
  #  @return
  #    Path to log file.
  @staticmethod
  def getLogFile():
    return _Logger.logfile

  ## Checks if debugging is enabled.
  #
  #  @return
  #  True if logging level is >= _LogLevel.DEBUG.
  @staticmethod
  def debugging():
    return _Logger.getLevel() >= _LogLevel.DEBUG

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
      lvl = _LogLevel.INFO
    if _Logger.loglevel == _LogLevel.SILENT or _Logger.loglevel < lvl:
      return
    stream = sys.stdout
    if lvl == _LogLevel.ERROR:
      stream = sys.stderr
    prefix = (_LogLevel.toString(lvl) + ":")
    if self.id:
      prefix += " (" + self.id + ")"
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
    if _Logger.logfile and os.path.isfile(_Logger.logfile):
      fileio.appendFile(_Logger.logfile, msg)

  ## Logs a message at debug level.
  #
  #  @param msg
  #    Text of message to log.
  #  @param details
  #    Extra details to append to message.
  #  @param newline
  #    If true, appends a newline to end of message.
  def debug(self, msg, details=None, newline=False):
    self.log(_LogLevel.DEBUG, msg, details, newline)

  ## Logs a message at info level.
  #
  #  @param msg
  #    Text of message to log.
  #  @param details
  #    Extra details to append to message.
  #  @param newline
  #    If true, appends a newline to end of message.
  def info(self, msg, details=None, newline=False):
    self.log(_LogLevel.INFO, msg, details, newline)

  ## Logs a message at warning level.
  #
  #  @param msg
  #    Text of message to log.
  #  @param details
  #    Extra details to append to message.
  #  @param newline
  #    If true, appends a newline to end of message.
  def warn(self, msg, details=None, newline=False):
    self.log(_LogLevel.WARN, msg, details, newline)

  ## Logs a message at error level.
  #
  #  @param msg
  #    Text of message to log.
  #  @param details
  #    Extra details to append to message.
  #  @param newline
  #    If true, appends a newline to end of message.
  def error(self, msg, details=None, newline=False):
    self.log(_LogLevel.ERROR, msg, details, newline)

  ## Logs a message denoting deprecation of an element.
  #
  #  @param module
  #    Name of module containing element.
  #  @param name
  #    Element name.
  #  @param alt
  #    Information about alternatives.
  #  @param newline
  #    If true, appends a newline to end of message.
  def deprecated(self, module, name, alt=None, newline=False):
    msg = module + "." + name + " is deprecated"
    if alt:
      msg += ", use " + alt + " instead"
    self.warn(msg, newline)


## Retrieves a logger.
#
#  @param _id
#    Optional ID to display in log messages.
#  @return
#    Logger instance.
def getLogger(_id=None):
  return _Logger(_id)
