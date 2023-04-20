
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## Parsing & writing configuration.
#
#  @module dbr.config

import os
import sys

import wx

import libdbr.config

from dbr.functions   import GetBoolean
from dbr.functions   import GetIntTuple
from dbr.functions   import IsIntTuple
from dbr.language    import GT
from libdbr          import paths
from libdbr          import strings
from libdbr.fileio   import readFile
from libdbr.fileio   import writeFile
from libdbr.logger   import Logger


__logger = Logger(__name__)

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
default_config_dir = "{}/.config/debreate".format(paths.getUserHome())
default_config = "{}/config".format(default_config_dir)

# helper class
class _IntPair:
  def __init__(self, value):
    Logger(__name__).deprecated(_IntPair, alt="libdbr.types.Pair")

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
  "workingdir": paths.getUserHome(),
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
  cfg_user = libdbr.config.get("user")
  return {
    "center": cfg_user.getBool("center", __defaults["center"]),
    "maximize": cfg_user.getBool("maximize", __defaults["maximize"]),
    "position": tuple(cfg_user.getList("position", __defaults["position"], sep=",", handler=int)),
    "size": tuple(cfg_user.getList("size", __defaults["size"], sep=",", handler=int)),
    "workingdir": cfg_user.getValue("workingdir", __defaults["workingdir"]),
    "tooltips": cfg_user.getBool("tooltips", __defaults["tooltips"])
  }

def getDefault(key):
  if key not in __defaults:
    return None
  return __defaults[key]


## @todo Doxygen
def SetDefaultConfigKey(key, value):
  # ~ __logger.deprecated(SetDefaultConfigKey, alt=libdbr.config)

  __defaults[key] = strings.toString(value)


## Function used to create the initial configuration file.
#
#  @param conf
#    File to be written.
#  @return
#    ConfCode.
#  @deprecated
def initialize(conf=default_config):
  __logger.deprecated(initialize)

  cfg_user = libdbr.config.get("user")
  cfg_user.setFile(conf)
  for V in __defaults:
    cfg_user.setValue(V, __defaults[V])
  cfg_user.save()
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
