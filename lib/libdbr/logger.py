
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

import errno
import os
import sys

from libdbr          import dateinfo
from libdbr          import fileio
from libdbr          import paths
from libdbr.dateinfo import dtfmt


## Logs events to console & log file.
#
#  TODO:
#    - add timestamps
#    - show module name
class LogLevel:
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
    return LogLevel.INFO

  @staticmethod
  def toString(loglevel):
    for st in LogLevel.strings:
      if LogLevel.strings[st] == loglevel:
        if st == "WARN":
          st = "WARNING"
        return st
    return LogLevel.getDefault()

  @staticmethod
  def fromString(st):
    return LogLevel.strings[st] if st in LogLevel.strings else LogLevel.getDefault()

class Logger:
  loglevel = LogLevel.INFO
  logfile = None
  logsdir = None

  def startLogging(self, logsdir=None):
    self.logsdir = logsdir

    if not os.path.isdir(self.logsdir):
      if os.path.exists(self.logsdir):
        self.error("cannot create logs directory, file exists: {}".format(self.logsdir))
        sys.exit(errno.EEXIST)
      os.makedirs(self.logsdir)
    date_start = dateinfo.getDate(dtfmt.LOG)
    time_start = dateinfo.getTime(dtfmt.LOG)
    self.logfile = paths.join(self.logsdir, date_start+".txt")

    date_time = "{} {}".format(date_start, time_start)
    header = "--------------- Log Start: {} ---------------\n".format(date_time)
    # write header to log file
    fileio.appendFile(self.logfile, header)

  def endLogging(self):
    if not self.logfile or not os.path.isfile(self.logfile):
      # initialization failed or user deleted log file
      return
    date_time = "{} {}".format(dateinfo.getDate(dtfmt.LOG), dateinfo.getTime(dtfmt.LOG))
    footer = "\n--------------- Log End:   {} ---------------\n\n".format(date_time)
    fileio.appendFile(self.logfile, footer)

  def setLevel(self, loglevel):
    if type(loglevel) == str:
      loglevel_up = loglevel.upper()
      if not loglevel_up in LogLevel.strings:
        self.warn("invalid logging level: " + loglevel)
      loglevel = LogLevel.fromString(loglevel_up)
    self.loglevel = loglevel

  def getLevel(self):
    return self.loglevel

  def getLogFile(self):
    return self.logfile

  def debugging(self):
    return self.getLevel() >= LogLevel.DEBUG

  def log(self, lvl, msg="", details=None, newline=False):
    if not msg:
      msg = lvl
      lvl = LogLevel.INFO
    if self.loglevel == LogLevel.SILENT or self.loglevel < lvl:
      return
    stream = sys.stdout
    if lvl == LogLevel.ERROR:
      stream = sys.stderr
    msg = (LogLevel.toString(lvl) + ":").ljust(9) + msg
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
    if self.logfile and os.path.isfile(self.logfile):
      fileio.appendFile(self.logfile, msg)

  def debug(self, msg, details=None, newline=False):
    self.log(LogLevel.DEBUG, msg, details, newline)

  def info(self, msg, details=None, newline=False):
    self.log(LogLevel.INFO, msg, details, newline)

  def warn(self, msg, details=None, newline=False):
    self.log(LogLevel.WARN, msg, details, newline)

  def error(self, msg, details=None, newline=False):
    self.log(LogLevel.ERROR, msg, details, newline)

  def deprecated(self, module, name, alt=None, newline=False):
    msg = module + "." + name + " is deprecated"
    if alt:
      msg += ", use " + alt + " instead"
    self.warn(msg, newline)


# exported instance
instance = None
def getLogger(name=None):
  global instance
  if not instance:
    instance = Logger()
  return instance
