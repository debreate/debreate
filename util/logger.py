
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: docs/LICENSE.txt for details.               *
# ****************************************************

# TODO: replace calls to dbr.log

import errno, os, sys

from globals          import paths
from globals.dateinfo import GetDate
from globals.dateinfo import GetTime
from globals.dateinfo import dtfmt
from globals.fileio   import AppendFile


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

  def startLogging(self):
    dir_logs = paths.getLogsDir()
    if not os.path.isdir(dir_logs):
      if os.path.exists(dir_logs):
        self.error("cannot create logs directory, file exists: {}".format(dir_logs))
        sys.exit(errno.EEXIST)
      os.makedirs(dir_logs)
    date_start = GetDate(dtfmt.LOG)
    time_start = GetTime(dtfmt.LOG)
    self.logfile = os.path.join(dir_logs, date_start+".txt")

    date_time = "{} {}".format(date_start, time_start)
    header = "--------------- Log Start: {} ---------------\n".format(date_time)
    # write header to log file
    AppendFile(self.logfile, header, noStrip="\n")

  def endLogging(self):
    if not self.logfile or not os.path.isfile(self.logfile):
      # initialization failed or user deleted log file
      return
    date_time = "{} {}".format(GetDate(dtfmt.LOG), GetTime(dtfmt.LOG))
    footer = "\n--------------- Log End:   {} ---------------\n\n".format(date_time)
    AppendFile(self.logfile, footer, noStrip="\n")

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

  def log(self, lvl, msg=""):
    if not msg:
      msg = lvl
      lvl = LogLevel.INFO
    if self.loglevel == LogLevel.SILENT or self.loglevel < lvl:
      return
    stream = sys.stdout
    if lvl == LogLevel.ERROR:
      stream = sys.stderr
    msg = (LogLevel.toString(lvl) + ":").ljust(9) + msg
    stream.write(msg + "\n")
    # output to log file
    if self.logfile and os.path.isfile(self.logfile):
      AppendFile(self.logfile, msg, noStrip="\n")

  def debug(self, msg):
    self.log(LogLevel.DEBUG, msg)

  def info(self, msg):
    self.log(LogLevel.INFO, msg)

  def warn(self, msg):
    self.log(LogLevel.WARN, msg)

  def error(self, msg):
    self.log(LogLevel.ERROR, msg)

  def deprecated(self, module, name, alt=None):
    msg = module + "." + name + " is deprecated"
    if alt:
      msg += ", use " + alt + " instead"
    self.warn(msg)


# exported instance
instance = None
def getLogger(name=None):
  global instance
  if not instance:
    instance = Logger()
  return instance
