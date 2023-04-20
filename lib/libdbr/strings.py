
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## String handling.
#
#  @module libdbr.strings

import re
import sys
import traceback


## Debugging helper function.
def __printError(msg):
  sys.stderr.write("ERROR: ({}) {}\n".format(__name__, msg))


__from_handlers = {"str": str.__call__}

## Ensures working with strings.
#
#  @param st
#    String or bytes object to check.
#  @return
#    String value.
def checkString(st):
  if type(st) == bytes:
    st = st.decode("utf-8")
  if type(st) != str:
    raise TypeError("value must be string, found '{}'".format(type(st)))
  return st

## Convert a compatible type to string.
#
#  @param obj
#    Object to be converted.
#  @param sep
#    Separation delimiter in case of obj being a list type.
#  @return
#    String representation.
def toString(obj, sep=""):
  res = ""
  o_type = type(obj)
  if o_type in (list, tuple, dict):
    for i in obj:
      if res:
        res += sep
      res += toString(i) # FIXME: do we need to pass 'sep' argument?
  elif o_type not in (str, bytes):
    res = str(obj)
  else:
    res = obj
  return checkString(res)

## Converts a string to another type.
#
#  @param st
#    String to be converted.
#  @param handler
#    Handler determining return type.
#  @return
#    Type instance represented by `st`.
def fromString(st, handler=str):
  if handler == str:
    # no need to convert to same type
    return st
  if handler.__name__ in __from_handlers:
    return __from_handlers[handler.__name__](st)
  return handler(st)

## Converts a string value to boolean.
#
#  Note: if string is not a compatible boolean format, False is returned
#
#  @param st
#    String to parse.
def boolFromString(st):
  if type(st) != str:
    st = toString(st)
  if st.lower() in ("true", "yes"):
    return True
  try:
    tmp = float(st)
    return tmp != 0
  except ValueError:
    pass
  return False
__from_handlers["bool"] = boolFromString

## Converts a string to integer.
#
#  @param st
#    String to parse.
#  @param verbose
#    Print extra debugging information.
#  @return
#    Integer value.
def intFromString(st, verbose=False):
  # ~ i = None
  # ~ try:
    # ~ i = int(st)
  # ~ except ValueError as e:
    # ~ msg = "cannot convert '{}' to type 'int'\n{}".format(st, traceback.format_exc)
    # ~ if verbose:
      # ~ __printError(msg)
    # ~ return e, msg
  # ~ return i
  res = floatFromString(st, verbose)
  if type(res) == float:
    return int(res)
  return res
__from_handlers["int"] = intFromString

## Converts a string to float.
#
#  @param st
#    String to parse.
#  @param verbose
#    Print extra debugging information.
#  @return
#    Ingeger value.
def floatFromString(st, verbose=False):
  f = None
  try:
    f = float(st)
  except ValueError as e:
    if verbose:
      __printError("cannot convert '{}' to type 'float'\n{}".format(st, traceback.format_exc))
    return None
  return f
__from_handlers["float"] = floatFromString

## Converts a string to list.
#
#  @param st
#    String to parse.
#  @param sep
#    Delimiting character to separate string.
#  @param _type
#    Data type that list should contain.
#  @param verbose
#    Print extra debugging information.
#  @return
#    List or tuple with error code & message.
def listFromString(st, sep=";", _type=str, verbose=False):
  l = []
  for c in st.split(sep):
    try:
      res = __from_handlers[_type.__name__](c)
      if res != None:
        l.append(res)
    except ValueError as e:
      if verbose:
        __printError("cannot convert '{}' to type '{}'\n{}".format(c, _type, traceback.format_exc))
      return None
  return l or None
__from_handlers["list"] = listFromString
__from_handlers["tuple"] = listFromString
# FIXME: 'dict' should have a special handler
__from_handlers["dict"] = listFromString

## Converts a string to a list of integers.
#
#  @param st
#    String to parse.
#  @param sep
#    Delimiting character to separate string.
#  @param _type
#    Data type that list should contain.
#  @param verbose
#    Print extra debugging information.
#  @return
#    List or tuple.
def intListFromString(st, sep=";", verbose=False):
  return listFromString(st, sep, int, verbose)
__from_handlers["int_list"] = intListFromString

# hack for backward compatibility with Debreate's old config management
# ~ int_list = types.new_class("int_list")
def dummyFunction(lst):
  return tuple(lst) if lst else ()
int_list = dummyFunction
int_list.__name__ = "int_list"

__sgrstyles = {
  "end": 0,
  "bold": 1,
  "faint": 2,
  "em": 3,
  "ital": 3,
  "under": 4,
  "sblink": 5,
  "rblink": 6,
  "invert": 7,
  "conceal": 8,
  "xout": 9,
  "pfont": 10,
  "fraktur": 20,
  "dunder": 21,
  "/bold": 22,
  "/faint": 22,
  "/em": 23,
  "/ital": 23,
  "/fraktur": 23,
  "/under": 24,
  "/blink": 25,
  # 26?
  "/invert": 27,
  "/conceal": 28,
  "/xout": 29,
  "black": 30,
  "red": 31,
  "green": 32,
  "yellow": 33,
  "blue": 34,
  "magenta": 35,
  "cyan": 36,
  "white": 37,
  # 38 TODO: set custom color with '5;<n>' or '2;<r>;<g>;<b>'
  "/fg": 39,
  "black-bg": 40,
  "red-bg": 41,
  "green-bg": 42,
  "yellow-bg": 43,
  "blue-bg": 44,
  "magenta-bg": 45,
  "cyan-bg": 46,
  "white-bg": 47,
  # 48 TODO: same as 38
  "/bg": 49,
  # 50?
  "frame": 51,
  "circle": 52,
  "over": 53,
  "/frame": 54,
  "/circle": 54,
  "/over": 55
  # more?
}

for _idx in range(1, 10):
  __sgrstyles["afont{}".format(_idx)] = _idx + 10
for _idx in range(1, 9):
  __sgrstyles["fg{}".format(_idx)] = _idx + 29
for _idx in range(1, 9):
  __sgrstyles["bg{}".format(_idx)] = _idx + 39

## Formats a stylized string for terminal output.
#
#  @param st
#    String to be formatted.
#  @return
#    String formatted using ANSI escape codes (Select Graphic Rendition).
def sgr(st):
  for key in __sgrstyles:
    st = st.replace("<{}>".format(key), "\033[{}m".format(__sgrstyles[key]))
  return st

## Checks if a string is only whitespace.
#
#  @param st
#    String or bytes object to check.
#  @return
#    `True` if string contains only whitespace characters.
def isEmpty(st):
  # ensure working with string
  st = checkString(st)
  return st.strip() == ""

## Checks if a string represents an integer value.
#
#  @param st
#    String or bytes object to check.
#  @return
#    `True` if string contains only integers.
def isInteger(st):
  # ensure working with string
  st = checkString(st)
  try:
    int(st)
  except ValueError:
    return False
  return True

## Checks if a string represents a numberic value.
#
#  @param st
#    String or bytes object to check.
#  @return
#    `True` if string can be parsed as a float.
def isNumeric(st):
  # ensure working with string
  st = checkString(st)
  try:
    float(st)
  except ValueError:
    return False
  return True

## Checks if string contains any alphabetic characters.
#
#  @param st
#    String or bytes object to check.
#  @return
#    `True` if any alphabet characters exist in string.
def hasAlpha(st):
  st = toString(st)
  return re.search("[A-z]", st) != None
