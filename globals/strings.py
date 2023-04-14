
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module globals.strings
#
#  Module for manipulating strings & string lists

import sys

import libdbr.strings

from libdbr.logger import Logger


__logger = Logger(__name__)

## Checks if a text string is empty.
#
#  @param text
#    The string to be checked.
#  @deprecated
#    Use `libdbr.strings.isEmpty`.
def TextIsEmpty(text):
  __logger.deprecated(TextIsEmpty, alt=libdbr.strings.isEmpty)

  return not text.strip(" \t\n\r")


## Removes empty lines from a string or string list.
#
#  @param text
#    String or \b \e list to be checked.
#  @return
#    String or \b \e tuple with empty lines removed.
def RemoveEmptyLines(text):
  fmt_string = False

  if IsString(text):
    fmt_string = True
    text = text.split("\n")

  elif isinstance(text, tuple):
    text = list(text)

  # Iterate in reverse to avoid skipping indexes
  for INDEX in reversed(range(len(text))):
    if libdbr.strings.isEmpty(text[INDEX]):
      text.pop(INDEX)

  if fmt_string:
    return "\n".join(text)

  return tuple(text)


## Checks if object is a string instance.
#
#  Compatibility function for legacy Python versions.
#
#  @param text
#    String to check.
def IsString(text):
  return isinstance(text, str)


## Converts an object to a string instance.
#
#  Compatibility function for legacy Python versions.
#
#  @param item
#    Instance to be converted to string.
#  @return
#    Compatible string.
#  @deprecated
#    Use `libdbr.strings.toString`.
def ToString(item):
  __logger.deprecated(ToString, alt=libdbr.strings.toString)

  return libdbr.strings.toString(item)


## @deprecated
#    Use `libdbr.strings.toString`.
def GS(st):
  __logger.deprecated(GS, alt=libdbr.strings.toString)

  return str(st)


## Tests if a string can be converted to int or float.
#
#  @param string
#    String to be tested.
#  @deprecated
#    Use `libdbr.strings.isNumeric`.
def StringIsNumeric(string):
  __logger.deprecated(StringIsNumeric, alt=libdbr.strings.isNumeric)

  try:
    float(string)
    return True

  except ValueError:
    return False


## Tests if a string is formatted for versioning.
#
#  @param string
#    String to be checked.
#  @return
#    `True` if string is formatted to represent versioning information.
def StringIsVersioned(string):
  for P in string.split("."):
    if not P.isnumeric():
      return False

  return True


## Retrieves a class instance's module name string.
#
#  @param item
#    Object instance.
#  @param className
#    If `True`, returns class object's name instead of module name.
#  @param full
#    If `True`, return entire module/class string without parsing.
#  @return
#    String representation.
def GetModuleString(item, className=False, full=False):
  module = ToString(item.__class__)

  # Strip extra characters
  if "'" in module:
    module = module[module.index("'")+1:].split("'")[0]

  if full:
    return module

  module = module.split(".")

  if className:
    return module[-1]

  return ".".join(module[:-1])


## Retrieves an instance's method name in the format of "Class.Method".
#
#  @param function
#    Function object.
#  @param includeModule
#    Prepend module name to string for class methods.
#  @return
#    String representation.
def GetFunctionString(function, includeModule=False):
  function = ToString(function).strip("<>")

  if function.startswith("bound method "):
    function = function.split("<")

    module = function[1].split(";")[0]
    function = function[0].lstrip("bound method ").split(" ")[0]

    if includeModule:
      class_name = function.split(".")[0]

      if ".{}".format(class_name) in module:
        module = module.replace(".{}".format(class_name), "")

      function = "{}.{}".format(module, function)

  else:
    function = function.split(" ")[1]

  return function
