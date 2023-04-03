
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

import libdbr

from libdbr.fileio import readFile
from libdbr.fileio import writeFile
from libdbr.logger import getLogger


__logger = getLogger()
__config_file = None
__config_cache = {}

## Sets path to config file for read/write.
#
#  @param filepath
#    String path to file.
#  @return
#    libdbr.config module.
def setFile(filepath):
  global __config_file
  __config_file = filepath
  return libdbr.config

## Parses config file data into a managable list.
#
#  @return
#    List of file contents.
#  @param filepath
#    Parse filepath instead of path set with setFile
def __parseLines(filepath=None):
  if filepath != None:
    __config_file = filepath
  if not __config_file:
    __logger.error("cannot parse config, file path not set with 'setFile' & 'filepath' arg not set")
    return []
  if not os.path.isfile(__config_file):
    __logger.error("cannot parse config, file doesn't exist: {}".format(__config_file))
    return []
  lines_in = readFile(__config_file).split("\n")
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
    __logger.error("key '{}' not found in config and default value not set".format(key))
    return
  return value

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
    key = lines_old[0]
    value = lines_old[1]
    if key in tmp:
      value = tmp[key]
      del tmp[key]
    lines.append(key + " = " + value)
  # new keys
  for key in tmp:
    lines.append(key + " = " + tmp[key])
  writeFile(__config_file, lines)
  # update cache
  if update:
    load()
