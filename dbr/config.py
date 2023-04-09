## \package dbr.config
#
#  Parsing & writing configuration.

# MIT licensing
# See: docs/LICENSE.txt


import os, sys, wx

from dbr.functions   import GetBoolean
from dbr.functions   import GetIntTuple
from dbr.functions   import IsIntTuple
from dbr.language    import GT
from globals.strings import GS
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

# name = (function, default value)
# ~ default_config_values = {
  # ~ "center": (GetBoolean, True),
  # ~ "maximize": (GetBoolean, False),
  # ~ "position": (GetIntTuple, (0, 0)),
  # ~ "size": (GetIntTuple, (800, 640)),
  # ~ "workingdir": (GS, paths.getHomeDir()),
  # ~ "tooltips": (GetBoolean, True),
# ~ }

__defaults = {
  "center": "True",
  "maximize": "False",
  "position": "0,0",
  "size": "800,640",
  "workingdir": paths.getHomeDir(),
  "tooltips": "True"
}

def getConfiguration():
  if not config.getFile():
    config.setFile(default_config)
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

  # ~ global default_config_values

  # Default type is string
  func = GS

  if isinstance(value, bool):
    func = GetBoolean

  elif IsIntTuple(value):
    func = GetIntTuple

  # ~ default_config_values[key] = (func, value,)
  __defaults[key] = strings.toString(value)


## Function used to create the initial configuration file
#
#  \param conf
#  	\b \e str : File to be written
#  \return
#  	\b \e ConfCode
def InitializeConfig(conf=default_config):
  config.setFile(conf)
  for V in default_config_values:
    config.setValue(V, default_config_values[V][1])
  config.save()
  return ConfCode.SUCCESS


## Retrieves default configuration value for a key
#
#  \param key
#  	\b \e str : Key to check
#  \return
#  	Default value for the key or ConfCode.KEY_NO_EXIST
def GetDefaultConfigValue(key):
  if key in default_config:
    return default_config_values[key][1]

  return ConfCode.KEY_NO_EXIST


## Checks if value type is correct
def _check_config_values(keys):
  for KEY in keys:
    try:
      if not isinstance(keys[KEY], type(default_config_values[KEY][1])):
        sys.stderr.write("Config error:\n")
        sys.stderr.write("  Key: {}\n".format(KEY))
        sys.stderr.write("  Value: {}\n".format(keys[KEY]))
        sys.stderr.write("  Value type: {}\n".format(type(keys[KEY])))
        sys.stderr.write("  Target type: {}\n".format(type(default_config_values[KEY][1])))
        sys.stderr.write("Bad value type\n")

        return False

    except KeyError:
      sys.stderr.write("Config error:\n")
      sys.stderr.write("  KeyError: {}\n".format(KEY))

      return False

  return True


# ~ ## Reads in all values found in configuration file
# ~ #
# ~ #  \return
# ~ #  Configuration keys found in config file or None if error occurred
# ~ def GetAllConfigKeys():
  # ~ logger.deprecated(__name__, GetAllConfigKeys.__name__, "libdbr.config.getKeys")

  # ~ if not config.getFile():
    # ~ config.setFile(default_config)

  # ~ keys = {}

  # ~ # what a mess this is!

  # ~ # Read key/values from configuration file
  # ~ for KEY in default_config_values:
    # ~ handler = type(default_config_values[KEY][1])
    # ~ # hack
    # ~ if handler in (list, tuple):
      # ~ handler = strings.int_list
    # ~ default_value = None
    # ~ if KEY in default_config_values:
      # ~ default_value = strings.toString(default_config_values[KEY][1], sep=",")
    # ~ keys[KEY] = strings.fromString(config.getValue(KEY, default_value), handler=handler)
    # ~ if type(keys[KEY]) != handler:
      # ~ keys[KEY] = handler(keys[KEY])

  # ~ if not _check_config_values(keys):
    # ~ return None

  # ~ return keys
