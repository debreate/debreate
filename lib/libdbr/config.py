
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

# configuration file handling

# TODO: create instantiable class to allow multiple configuration files

import os
import re

from libdbr        import strings
from libdbr.fileio import readFile
from libdbr.fileio import writeFile
from libdbr.logger import Logger


__logger = Logger(__name__)
__config_file = None
__config_cache = {}
__config_defaults = {}

## Sets path to config file for read/write.
#
#  @param filepath
#    String path to file.
def setFile(filepath):
  global __config_file
  __config_file = filepath

## Retrieved configured file.
#
#  @return
#    Path to configuration file.
def getFile():
  return __config_file

## Retrieves the default value for a key.
#
#  @param key
#    Key identifier.
#  @return
#    Default value or `None` if key not set.
def getDefault(key):
  if key in __config_defaults:
    return __config_defaults[key]
  return None

## Retrieves entire dictionary of default values.
#
#  @return
#    Dictionary.
def getDefaults():
  return __config_defaults

## Stores a default value to be used for key.
#
#  @param key
#    Key identifier.
#  @param value
#    Value to be stored.
def setDefault(key, value):
  __config_defaults[key] = value

## Stores a group of default values.
#
#  @param defaults
#    Dictionary containing keys & values.
def setDefaults(defaults):
  for key in defaults:
    __config_defaults[key] = defaults[key]

## Unsets a default value.
#
#  @param key
#    Key identifier.
def unsetDefault(key):
  if key in __config_defaults:
    del __config_defaults[key]

## Clears all stored defaults.
def clearDefaults():
  for key in __config_defaults:
    del __config_defaults[key]

## Parses config file data into a managable list.
#
#  @return
#    List of file contents.
#  @param filepath
#    Parse filepath instead of path set with setFile
def __parseLines(filepath=None):
  if filepath == None:
    filepath = __config_file
  if not filepath:
    __logger.error("cannot parse config, file path not set with 'setFile' & 'filepath' arg not set")
    return []
  if not os.path.isfile(filepath):
    __logger.error("cannot parse config, file doesn't exist: {}".format(filepath))
    return []
  lines_in = readFile(filepath).split("\n")
  lines = []
  lidx = 0
  for line_orig in lines_in:
    line = line_orig.strip()
    if not line:
      # preserve empty lines
      lines.append("")
      continue
    if line.startswith("#"):
      # preserve comments
      lines.append(line)
      continue
    # valid config lines must include '=' & start with alphabetical character
    if not "=" in line or not line[0].isalpha:
      __logger.error("malformed line in config ({}): '{}'".format(lidx, line_orig))
      continue
    key_value = line.split("=", 1)
    key = key_value[0].strip()
    value = key_value[1].strip()
    # check for empty key or value or invalid characters in key
    if not key or not value or re.search(r" |\t", key):
      __logger.error("malformed line in config ({}): '{}'".format(lidx, line_orig))
      continue
    lines.append((key, value))
  return lines

## Parses config data from file into a dictionary.
#
#  @return
#    Dictionary of key-value pairs.
#  @param filepath
#    Parse filepath instead of path set with setFile
def parseFile(filepath=None):
  lines = __parseLines(filepath)
  tmp = {}
  for line in lines:
    # get key-value pairs
    if type(line) == str:
      continue
    key = line[0]
    value = line[1]
    if key in tmp:
      __logger.warn("duplicate key '{}' in config".format(key))
    tmp[key] = value
  return tmp

## Loads config data from file into memory.
def load():
  global __config_cache
  __config_cache = parseFile()

## Retrievies a value from config.
#
#  @todo add functions for getInt, getFloat, getBool, etc.
#  @param key
#    Key identifier.
#  @param default
#    Default value if key is not present in config.
#  @param filepath
#    Parse filepath instead of path set with setFile
def getValue(key, default=None, filepath=None):
  tmp = dict(__config_cache)
  if not tmp or filepath != None:
    tmp = parseFile(filepath)
  if key not in tmp:
    value = default
  else:
    value = tmp[key]
  if value == None:
    if key in __config_defaults:
      return __config_defaults[key]
    __logger.error("key '{}' not found in config and default value not set".format(key))
    return None
  return value

## Retrievies a key=value formatted string from config.
#
#  Entries not containing '=' denoting a value are set as flags.
#
#  @param key
#    Key identifier.
#  @param filepath
#    Parse filepath instead of path set with setFile
#  @param sep
#    Delimiter to use for splitting strings.
#  @param _type
#    Convert values to specified data type.
#  @return
#    Dictionary or None.
def getKeyedValue(key, filepath=None, sep=";", _type=str):
  value = getValue(key, "", filepath).split(sep)
  if not value:
    return
  res = {}
  for li in value:
    li = li.strip()
    if "=" not in li:
      # set flag for non-key=value types
      res[li] = True
    else:
      tmp = li.split("=", 1)
      res[tmp[0].strip()] = _type(tmp[1].strip())
  return res

## Retrieves a boolean value from config.
#
#  @param key
#    Key identifier.
#  @param default
#    Default value if key is not present in config.
#  @param filepath
#    Parse filepath instead of path set with setFile.
#  @return
#    Boolean or tuple with error info.
def getBool(key, default=None, filepath=None):
  return strings.boolFromString(getValue(key, default, filepath))

## Retrieves an integer value from config.
#
#  @param key
#    Key identifier.
#  @param default
#    Default value if key is not present in config.
#  @param filepath
#    Parse filepath instead of path set with setFile.
#  @return
#    Boolean or tuple with error info.
def getInt(key, default=None, filepath=None):
  res = getFloat(key, default, filepath)
  if type(res) == tuple:
    return res
  return int(res)

## Retrieves a float value from config.
#
#  @param key
#    Key identifier.
#  @param default
#    Default value if key is not present in config.
#  @param filepath
#    Parse filepath instead of path set with setFile.
#  @return
#    Boolean or tuple with error info.
def getFloat(key, default=None, filepath=None):
  return strings.floatFromString(getValue(key, default, filepath))

## Retrievies configuration keys.
#
#  @return
#    Keys available in configuration.
def getKeys():
  return tuple(__config_cache)

## Sets value for a key in config.
#
#  'libdbr.config.save' must be called to update the file.
#
#  @param key
#    Key identifier.
#  @param value
#    Value to be set.
def setValue(key, value):
  if type(value) != str:
    value = strings.toString(value, ";")
  __config_cache[key.strip()] = value.strip()

## Writes configuration data to file.
#
#  @param update
#    If true, reloads new config into memory.
def save(update=True):
  if not __config_file:
    __logger.error("cannot save config, filepath not set with 'setFile'")
    return
  tmp = dict(__config_cache)
  lines_old = __parseLines()
  lines = []
  for line in lines_old:
    if type(line) == str:
      lines.append(line)
      continue
    key = line[0]
    value = line[1]
    if key in tmp:
      value = tmp[key]
      del tmp[key]
    lines.append(key + " = " + value)
  # new keys
  for key in tmp:
    lines.append(key + " = " + tmp[key])
  err, msg = writeFile(__config_file, lines)
  if err == 0:
    # update cache
    if update:
      load()
  return err, msg
