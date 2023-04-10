
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## Parsing & writing configuration.
#
#  @module dbr.config

import os, sys, wx

from dbr.functions   import GetBoolean
from dbr.functions   import GetIntTuple
from dbr.functions   import IsIntTuple
from dbr.language    import GT
from globals.strings import TextIsEmpty
from libdbr          import config
from libdbr          import paths
from libdbr          import strings
from libdbr.fileio   import readFile
from libdbr.fileio   import writeFile
from libdbr.logger   import Logger


logger = Logger(__name__)

## Configuration codes
class ConfCode:
  SUCCESS = 0
  ERR_READ = wx.NewId()
  ERR_WRITE = wx.NewId()
  FILE_NOT_FOUND = wx.NewId()
  WRONG_TYPE = wx.NewId()
  KEY_NO_EXIST = wx.NewId()
  KEY_NOT_DEFINED = wx.NewId()

  string = {
    SUCCESS: "SUCCESS",
    ERR_READ: "ERR_READ",
    ERR_WRITE: "ERR_WRITE",
    FILE_NOT_FOUND: "FILE_NOT_FOUND",
    WRONG_TYPE: "WRONG_TYPE",
    KEY_NO_EXIST: "KEY_NO_EXIST",
    KEY_NOT_DEFINED: "KEY_NOT_DEFINED",
  }

# Version of configuration to use
config_version = (1, 1)

# Default configuration
default_config_dir = "{}/.config/debreate".format(paths.getHomeDir())
default_config = "{}/config".format(default_config_dir)

# helper class
class _IntPair:
  def __init__(self, value):
    self.first = 0
    self.second = 0
    if type(value) in (list, tuple):
      self.first = value[0]
      self.second = value[1]
    else:
      tmp = value.split(",")
      self.first = tmp[0]
      if len(tmp) > 1:
        self.second = tmp[1]
    self.first = int(self.first)
    self.second = int(self.second)

  def __tuple__(self):
    return (self.first, self.second)

  def __call__(self):
    return self.__tuple__()

  def __str__(self):
    return str(self.__tuple__())

  def __eq__(self, other):
    return other == self.__tuple__()

__defaults = {
  "center": "True",
  "maximize": "False",
  "position": "0,0",
  "size": "800,640",
  "workingdir": paths.getHomeDir(),
  "tooltips": "True"
}

__defaults_handlers = {
  "center": bool,
  "maximize": bool,
  "position": _IntPair,
  "size": _IntPair,
  "workingdir": str,
  "tooltips": bool
}

def getConfiguration():
  return {
    "center": config.getBool("center", __defaults["center"]),
    "maximize": config.getBool("maximize", __defaults["maximize"]),
    "position": tuple(config.getList("position", __defaults["position"], ",", int)),
    "size": tuple(config.getList("size", __defaults["size"], ",", int)),
    "workingdir": config.getValue("workingdir", __defaults["workingdir"]),
    "tooltips": config.getBool("tooltips", __defaults["tooltips"])
  }

def getDefault(key):
  if key not in __defaults:
    return None
  return __defaults[key]


## TODO: Doxygen
def SetDefaultConfigKey(key, value):
  logger.deprecated(__name__, SetDefaultConfigKey.__name__, "libdbr.config")

  __defaults[key] = strings.toString(value)


## Function used to create the initial configuration file.
#
#  @param conf
#    File to be written.
#  @return
#    ConfCode.
def initialize(conf=default_config):
  config.setFile(conf)
  for V in __defaults:
    config.setValue(V, __defaults[V])
  config.save()
  return ConfCode.SUCCESS


## Retrieves default configuration value for a key.
#
#  @param key
#    Key identifier.
#  @return
#    Default value for the key or ConfCode.KEY_NO_EXIST.
def GetDefaultConfigValue(key):
  if key in default_config:
    # FIXME: may be returning wrong type
    return strings.fromString(__defaults[key], handler=__defaults_handlers[key])
  return ConfCode.KEY_NO_EXIST


## Checks if value type is correct
def _check_config_values(keys):
  for key in keys:
    try:
      handler = __defaults_handlers[key]
      value = handler(__defaults[key])
      if not isinstance(value, handler):
        sys.stderr.write("Config error:\n")
        sys.stderr.write("  Key: {}\n".format(key))
        sys.stderr.write("  Value: {}\n".format(value))
        sys.stderr.write("  Value type: {}\n".format(type(value)))
        sys.stderr.write("  Target type: {}\n".format(handler))
        sys.stderr.write("Bad value type\n")
        return False
    except KeyError:
      sys.stderr.write("Config error:\n")
      sys.stderr.write("  KeyError: {}\n".format(key))
      return False
  return True
