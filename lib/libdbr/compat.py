
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## Version handling.
#
#  @module libdbr.compat

from sys import version_info as py_version_info

from . import strings


## Checks for a compatible version.
#
#  @param found
#    The actual version.
#  @param req
#    The version requirement.
#  @param compare
#    Type of comparison.
#  @return
#    Comparison evaluation.
def checkVersion(found, req, compare=">="):
  met = False
  match compare:
    case "==":
      met = found == req
    case "!=":
      met = found != req
    case ">":
      met = found > req
    case "<":
      met = found < req
    case "<=":
      met = found <= req
    case _:
      # default
      met = found >= req
  return met

## Check for compatible Python version.
#
#  @param py_req
#    Minimum required version.
#  @return
#    Error code & message.
def checkPython(py_req):
  py_ver = py_version_info[0:3]
  if not checkVersion(py_ver, py_req):
    py_ver_st = strings.toString(py_ver, ".")
    py_req_st = strings.toString(py_req, ".")
    return 1, "incompatible Python version, need '{}', found '{}'".format(py_req, py_ver)
  return 0, None
