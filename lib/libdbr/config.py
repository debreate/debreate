
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## Configuration file handling.
#
#  @module libdbr.config

import errno
import os
import re

from .       import fileio
from .       import strings
from .logger import Logger
from .types  import Pair


_logger = Logger(__name__)

## Class representing a single configuration file.
#
#  @param filepath
#    Path to configuration file on filesystem.
#  @param default_section
#    Name to use for default section.
#  @param load
#    Set to `False` to disable automatically loading file contents into memory.
class Config:
  def __init__(self, filepath, default_section="", load=True):
    self.__filepath = strings.checkString(filepath)
    self.__default_section = default_section
    self.__sections = {
      default_section: []
    }
    # don't require manually calling 'load' to prevent accidentally overwriting
    if load and os.path.isfile(filepath):
      self.load()

  def __str__(self):
    return str(self.__sections)

  def __eq__(self, other):
    if type(other) != Config:
      return False
    s_namesA = tuple(self.__sections)
    s_namesB = tuple(other._Config__sections)
    if len(s_namesB) != len(s_namesA):
      return False
    for s_name in s_namesA:
      if s_name not in s_namesB:
        return False
      linesA = list(self.__sections[s_name])
      linesB = list(other._Config__sections[s_name])
      for lset in (linesA, linesB):
        # ignore empty lines & comments
        for idx in reversed(range(len(lset))):
          li = lset[idx]
          if not li or (type(li) == str and li.startswith("#")):
            lset.pop(idx)
      if len(linesB) != len(linesA):
        return False
      for liA in linesA:
        found = False
        for liB in linesB:
          if liB == liA:
            found = True
            break
        if not found:
          return False
    return True

  ## Parses config file data into a managable list.
  #
  #  @return
  #    List of file contents.
  def __parse_lines(self):
    if not os.path.isfile(self.__filepath):
      raise FileNotFoundError("configuration file not found '{}'".format(self.__filepath))
    if not self.__filepath:
      raise OSError("cannot parse configuration from empty file path")

    lines_in = fileio.readFile(self.__filepath).split("\n")
    lines = []
    lidx = 0
    for line_orig in lines_in:
      lidx += 1
      li = line_orig.strip()
      if not li:
        # preserve empty lines
        lines.append("")
        continue
      if li.startswith("#") or (li.startswith("[") and li.endswith("]")):
        # preserve comments & section headers
        lines.append(li)
        continue
      # valid config lines must include '=' & start with alphabetical character
      if not "=" in li or not li[0].isalpha():
        _logger.warn("malformed line in config ({}:{}): '{}'"
            .format(self.__filepath, lidx, line_orig))
        continue
      key_value = li.split("=", 1)
      key = key_value[0].strip()
      value = key_value[1].strip()
      # check for empty key or value or invalid characters in key
      if not key or not value or re.search(r" |\t", key):
        _logger.warn("malformed line in config ({}:{}): '{}'"
            .format(self.__filepath, lidx, line_orig))
        continue
      lines.append(Pair(key, value))
    if len(lines) > 0 and lines[-1] == "":
      # strip trailing newline on load
      lines.pop(-1)
    return lines

  ## Adds a configuration section.
  #
  #  @param s_name
  #    Section identifier.
  #  @param s_contents
  #    Config values.
  def __add_section(self, s_name, s_contents):
    s_name = s_name or self.__default_section or ""
    if s_name in self.__sections:
      _logger.error("duplicate section name '{}' in configuration '{}'"
          .format(s_name, self.__filepath))
    self.__sections[s_name] = s_contents

  ## Parses loaded data & updates stored values.
  #
  #  @return
  #    Dictionary of key-value pairs.
  def __parse_data(self):
    lines = self.__parse_lines()
    self.__sections = {}
    s_name = None
    s_lines = []
    for li in lines:
      if type(li) == str and li.startswith("[") and li.endswith("]"):
        self.__add_section(s_name, s_lines)
        # start new section
        s_lines = []
        s_name = li.strip("[]")
        continue
      s_lines.append(li)
    # remaining
    if s_lines:
      self.__add_section(s_name, s_lines)

  ## Retrievies configuration file.
  #
  #  @return
  #    Path to configuration file.
  def getFile(self):
    return self.__filepath

  ## Sets file to use for configuration.
  #
  #  @param filepath
  #    Path to configuration file on filesystem.
  #  @param load
  #    Set to `False` to disable automatically loading file contents into memory.
  def setFile(self, filepath, load=True):
    self.__filepath = filepath
    if load and os.path.isfile(filepath):
      self.load()

  ## Loads contents from disk.
  def load(self):
    if not os.path.isfile(self.__filepath):
      return errno.ENOENT, "configuration file '{}' does not exist".format(self.__filepath)
    self.__parse_data()
    return 0, None

  ## Saves contents to disk.
  def save(self):
    data_out = []
    sections = dict(self.__sections)
    if self.__default_section in sections:
      if self.__default_section:
        data_out.append("[{}]".format(self.__default_section))
      for li in sections[self.__default_section]:
        if type(li) == Pair:
          data_out.append("{} = {}".format(li.first(), li.second()))
        else:
          data_out.append(li)
      del sections[self.__default_section]
    for s_name in sections:
      data_out.append("[{}]".format(s_name))
      for li in sections[s_name]:
        if type(li) == Pair:
          data_out.append("{} = {}".format(li.first(), li.second()))
        else:
          data_out.append(li)
    if len(data_out) > 0 and data_out[-1] != "":
      # add trailing newline
      data_out.append("")
    fileio.writeFile(self.__filepath, data_out)

  ## Sets a value in configuration.
  #
  #  @param key
  #    String identifier.
  #  @param value
  #    Value to be set.
  #  @param section
  #    Section name to be amended (default: "").
  #  @param sep
  #    For list types (default: ",").
  def setValue(self, key, value, section=None, sep=","):
    section = section or self.__default_section
    try:
      key = strings.checkString(key).strip()
    except ValueError:
      raise TypeError("'{}.{}' parameter 'key' must be a string, found '{}'"
          .format(Config.__name__, setValue.__name__, type(key)))
    conf = self.__sections[section] if section in self.__sections else []
    insert_idx = len(conf)
    for idx in range(insert_idx):
      obj = conf[idx]
      if type(obj) == Pair and obj[0] == key:
        # replace old value
        conf.pop(idx)
        insert_idx = idx
        break
    conf.insert(insert_idx, Pair(key, strings.toString(value, sep=sep)))
    self.__sections[section] = conf

  ## Retreives a string value from config.
  #
  #  @param key
  #    String identifier.
  #  @param default
  #    Default value to return if key not found (default: `None`).
  #  @param section
  #    Section from which to get value (default: "").
  #  @return
  #    Set value or `None`.
  def getValue(self, key, default=None, section=None):
    section = section or self.__default_section
    if section not in self.__sections:
      if default != None:
        return default
      raise KeyError("section '{}' not found in config '{}'".format(section, self.__filepath))

    s_data = self.__sections[section]
    for li in s_data:
      if type(li) != Pair:
        continue
      if li.first() == key:
        return li.second()

    if default == None:
      suffix = self.__filepath
      if section:
        suffix = "section '{}:{}".format(suffix, section)
      else:
        suffix = "'" + suffix
      suffix += "'"
      raise KeyError("key '{}' not found in config {} and 'default' not set".format(key, suffix))
    return default

  ## Retreives a boolean value from config.
  #
  #  @param key
  #    String identifier.
  #  @param default
  #    Default value to return if key not found (default: `None`).
  #  @param section
  #    Section from which to get value (default: "").
  #  @return
  #    Set value or `None`.
  def getBool(self, key, default=None, section=None):
    return strings.boolFromString(self.getValue(key, default, section))

  ## Retreives an integer value from config.
  #
  #  @param key
  #    String identifier.
  #  @param default
  #    Default value to return if key not found (default: `None`).
  #  @param section
  #    Section from which to get value (default: "").
  #  @return
  #    Set value or `None`.
  def getInt(self, key, default=None, section=None):
    value = self.getFloat(key, default, section)
    # FIXME: not sure what I did this for?
    if type(value) == tuple:
      return value
    return int(value)

  ## Retreives a float value from config.
  #
  #  @param key
  #    String identifier.
  #  @param default
  #    Default value to return if key not found (default: `None`).
  #  @param section
  #    Section from which to get value (default: "").
  #  @return
  #    Set value or `None`.
  def getFloat(self, key, default=None, section=None):
    return strings.floatFromString(self.getValue(key, default, section))

  ## Retreives a list value from config.
  #
  #  @param key
  #    String identifier.
  #  @param default
  #    Default value to return if key not found (default: `None`).
  #  @param section
  #    Section from which to get value (default: "").
  #  @param sep
  #    List separation delimiter (default: ",").
  #  @param handler
  #    Method to convert parsed values type (default: `str`).
  #  @return
  #    Set value or `None`.
  def getList(self, key, default=None, section=None, sep=",", handler=str):
    return strings.listFromString(self.getValue(key, default, section), sep, handler)

  ## Retreives a key-value pair value from config.
  #
  #  @param key
  #    String identifier.
  #  @param default
  #    Default value to return if key not found (default: `None`).
  #  @param section
  #    Section from which to get value (default: "").
  #  @param sep
  #    List separation delimiter (default: ",").
  #  @param vsep
  #    Key-value pair separation delimiter (default: "=").
  #  @param handler
  #    Method to convert parsed values type (default: `str`).
  #  @return
  #    Set value or `None`.
  def getKeyedValue(self, key, default=None, section=None, sep=",", vsep="=", handler=str):
    value = self.getValue(key, default, section).split(sep)
    if not value:
      return
    res = {}
    for li in value:
      li = li.strip()
      if vsep not in li:
        # set flag for non-key=value types
        res[li] = True
      else:
        tmp = li.split("=", 1)
        res[tmp[0].strip()] = handler(tmp[1].strip())
    return res

  ## Retrievies configuration keys.
  #
  #  @param section
  #    Section from which to get value (default: "").
  #  @return
  #    Keys available in configuration.
  def getKeys(self, section=None):
    section = section or self.__default_section or ""
    if section not in self.__sections:
      raise KeyError("section '{}' not found in config '{}'".format(section, self.__filepath))

    keys = []
    for li in self.__sections[section]:
      if type(li) == Pair:
        keys.append(li.first())
    return tuple(keys)


## Cached configurations.
__configurations = {}

## Creates a new configuration instance & stores in cache.
#
#  @param _id
#    Configuration identifier.
#  @param filepath
#    Path to configuration file on filesystem.
#  @param default_section
#    Name to use for default section.
#  @return
#    New `Config` instance.
def add(_id, filepath, default_section=""):
  if _id in __configurations:
    _logger.warn("overwriting configuration '{}'".format(_id))
  __configurations[_id] = Config(filepath, default_section)
  return __configurations[_id]

## Retrieves a configuration from cache.
#
#  @param _id
#    Configuration identifier.
#  @return
#    `Config` instance or `None`.
def get(_id):
  if _id not in __configurations:
    _logger.warn("cannot return configuration, ID '{}' not found".format(_id))
    return None
  return __configurations[_id]

## Removes a configuration from cache.
#
#  @param _id
#    Configuration identifier.
#  @return
#    Copy of removed `Config` instance.
def pop(_id):
  if _id not in __configurations:
    _logger.warn("cannot remove configuration, ID '{}' not found".format(_id))
    return None
  cfg = __configurations[_id]
  del __configurations[_id]
  return cfg


__config_file = None
__config_cache = {}
__config_defaults = {}

## Sets path to config file for read/write.
#
#  @param filepath
#    String path to file.
#  @deprecated
#    Use `config.Config.setFile`.
def setFile(filepath):
  _logger.deprecated(setFile, alt=Config.setFile)

  global __config_file
  __config_file = filepath

## Retrieved configured file.
#
#  @return
#    Path to configuration file.
#  @deprecated
#    Use `config.Config.getFile`.
def getFile():
  _logger.deprecated(getFile, alt=Config.getFile)

  return __config_file

## Retrieves the default value for a key.
#
#  @param key
#    Key identifier.
#  @return
#    Default value or `None` if key not set.
#  @deprecated
def getDefault(key):
  _logger.deprecated(getDefault)

  if key in __config_defaults:
    return __config_defaults[key]
  return None

## Retrieves entire dictionary of default values.
#
#  @return
#    Dictionary.
#  @deprecated
def getDefaults():
  _logger.deprecated(getDefaults)

  return __config_defaults

## Stores a default value to be used for key.
#
#  @param key
#    Key identifier.
#  @param value
#    Value to be stored.
#  @deprecated
def setDefault(key, value):
  _logger.deprecated(setDefault)

  __config_defaults[key] = value

## Stores a group of default values.
#
#  @param defaults
#    Dictionary containing keys & values.
#  @deprecated
def setDefaults(defaults):
  _logger.deprecated(setDefaults)

  for key in defaults:
    __config_defaults[key] = defaults[key]

## Unsets a default value.
#
#  @param key
#    Key identifier.
#  @deprecated
def unsetDefault(key):
  _logger.deprecated(unsetDefault)

  if key in __config_defaults:
    del __config_defaults[key]

## Clears all stored defaults.
#
#  @deprecated
def clearDefaults():
  _logger.deprecated(clearDefaults)

  for key in __config_defaults:
    del __config_defaults[key]

## Parses config file data into a managable list.
#
#  @return
#    List of file contents.
#  @param filepath
#    Parse filepath instead of path set with setFile
#  @deprecated
#    Use `config.Config._Config__parse_lines`.
def __parseLines(filepath=None):
  _logger.deprecated(__parseLines, alt=Config._Config__parse_lines)

  if filepath == None:
    filepath = __config_file
  if not filepath:
    _logger.error("cannot parse config, file path not set with 'setFile' & 'filepath' arg not set")
    return []
  if not os.path.isfile(filepath):
    _logger.error("cannot parse config, file doesn't exist: {}".format(filepath))
    return []
  lines_in = fileio.readFile(filepath).split("\n")
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
    if not "=" in line or not line[0].isalpha():
      _logger.warn("malformed line in config ({}): '{}'".format(lidx, line_orig))
      continue
    key_value = line.split("=", 1)
    key = key_value[0].strip()
    value = key_value[1].strip()
    # check for empty key or value or invalid characters in key
    if not key or not value or re.search(r" |\t", key):
      _logger.warn("malformed line in config ({}): '{}'".format(lidx, line_orig))
      continue
    lines.append((key, value))
  return lines

## Parses config data from file into a dictionary.
#
#  @return
#    Dictionary of key-value pairs.
#  @param filepath
#    Parse filepath instead of path set with setFile
#  @deprecated
#    Use `config.Config._Config__parse_data`.
def parseFile(filepath=None):
  _logger.deprecated(parseFile, alt=Config._Config__parse_data)

  lines = __parseLines(filepath)
  tmp = {}
  for line in lines:
    # get key-value pairs
    if type(line) == str:
      continue
    key = line[0]
    value = line[1]
    if key in tmp:
      _logger.warn("duplicate key '{}' in config".format(key))
    tmp[key] = value
  return tmp

## Loads config data from file into memory.
#
#  @deprecated
#    Use `config.Config.load`.
def load():
  _logger.deprecated(load, alt=Config.load)

  global __config_cache
  __config_cache = parseFile()

## Retrievies a value from config.
#
#  @param key
#    Key identifier.
#  @param default
#    Default value if key is not present in config.
#  @param filepath
#    Parse filepath instead of path set with setFile
#  @deprecated
#    Use `config.Config.getValue`.
def getValue(key, default=None, filepath=None):
  _logger.deprecated(getValue, alt=Config.getValue)

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
    _logger.error("key '{}' not found in config and default value not set".format(key))
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
#  @deprecated
#    Use `config.Config.getKeyedValue`.
def getKeyedValue(key, filepath=None, sep=";", _type=str):
  _logger.deprecated(getKeyedValue, alt=Config.getKeyedValue)

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
#  @deprecated
#    Use `config.Config.getBool`.
def getBool(key, default=None, filepath=None):
  _logger.deprecated(getBool, alt=Config.getBool)

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
#  @deprecated
#    Use `config.Config.getInt`.
def getInt(key, default=None, filepath=None):
  _logger.deprecated(getInt, alt=Config.getInt)

  res = getFloat(key, default, filepath)
  # FIXME: not sure what I did this for?
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
#  @deprecated
#    Use `config.Config.getFloat`.
def getFloat(key, default=None, filepath=None):
  _logger.deprecated(getFloat, alt=Config.getFloat)

  return strings.floatFromString(getValue(key, default, filepath))

## Retrieves a list value from config.
#
#  @param key
#    Key identifier.
#  @param default
#    Default value if key is not present in config.
#  @param sep
#    List separation delimiter.
#  @param handler
#    Type handler for list contents.
#  @param filepath
#    Parse filepath instead of path set with setFile.
#  @return
#    List.
#  @deprecated
#    Use `config.Config.getList`.
def getList(key, default=None, sep=";", handler=str, filepath=None):
  _logger.deprecated(getList, alt=Config.getList)

  res = getValue(key, default)
  if res:
    res = strings.listFromString(res, sep, handler)
  return res

## Retrievies configuration keys.
#
#  @return
#    Keys available in configuration.
#  @deprecated
#    Use `config.Config.getKeys`.
def getKeys():
  _logger.deprecated(getKeys, alt=Config.getKeys)

  return tuple(__config_cache)

## Sets value for a key in config.
#
#  'libdbr.config.save' must be called to update the file.
#
#  @param key
#    Key identifier.
#  @param value
#    Value to be set.
#  @param sep
#    List delimiter.
#  @deprecated
#    Use `config.Config.setValue`.
def setValue(key, value, sep=";"):
  _logger.deprecated(setValue, alt=Config.setValue)

  if type(value) != str:
    value = strings.toString(value, sep)
  __config_cache[key.strip()] = value.strip()

## Writes configuration data to file.
#
#  @param update
#    If true, reloads new config into memory.
#  @deprecated
#    Use `config.Config.save`.
def save(update=True):
  _logger.deprecated(save, alt=Config.save)

  if not __config_file:
    _logger.error("cannot save config, filepath not set with 'setFile'")
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
  err, msg = fileio.writeFile(__config_file, lines)
  if err == 0:
    # update cache
    if update:
      load()
  return err, msg
