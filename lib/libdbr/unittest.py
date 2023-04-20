
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## Unit testing functions.
#
#  @module libdbr.unittest

import importlib
import re
import traceback
import types

from .logger import Logger


__logger = Logger(__name__)

## Run a Unit test.
#
#  @param test_name
#    Test module to import.
#  @param test_file
#    Optional filename to include in debugging output.
def runTest(test_name, test_file=None, verbose=False):
  if verbose:
    msg = "running test '{}'".format(test_name)
    if test_file:
      msg += " ({})".format(test_file)
    msg += " ..."
    __logger.info(msg)

  test_data = importlib.import_module(test_name)
  if test_data.__name__ != test_name:
    msg = "'{}' name mismatch ({}), cannot run test".format(test_name, test_data.__name__)
    __logger.error(msg)
    # FIXME: correct error code?
    return 1, msg
  if "init" not in test_data.__dict__:
    msg = "'{}' does not define funtion 'init', cannot run test".format(test_name)
    __logger.error(msg)
    # FIXME: correct error code?
    return 1, msg
  init_type = type(test_data.init)
  if init_type != types.FunctionType:
    msg = "'{}' requires 'init' to be a function but found type '{}', cannot run test".format(test_name, init_type)
    __logger.error(msg)
    # FIXME: correct error code?
    return 1, msg
  try:
    res = [test_data.init()]
  except:
    # XXX: is there a standard code for assertion errors?
    res = [1, traceback.format_exc()]
  err = None
  if len(res) > 1:
    err = res[1]
  res = res[0]

  if res == None:
    res = 0
  res_type = type(res)
  if res_type != int:
    msg = "'{}' test returned non-integer ({})".format(test_name, res_type)
    __logger.error(msg)
    # FIXME: correct error code?
    return 1, msg
  if res != 0:
    msg = "'{}' test returned error".format(test_name)
    if err:
      msg += ": " + err
    __logger.error(msg)
  return res, err


# -- assertion checking functions -- #

## Checks if a result is `True`.
#
#  @param a1
#    Expression result.
def assertTrue(a1):
  a_type = type(a1)
  if a_type != bool:
    raise AssertionError("expected 'bool' but got '{}'".format(a_type))
  if a1 != True:
    raise AssertionError("expected 'a1 == True' but got 'a1 == {}'".format(a1))

## Checks if a result is `False`.
#
#  @param a1
#    Expression result.
def assertFalse(a1):
  a_type = type(a1)
  if a_type != bool:
    raise AssertionError("expected 'bool' but got '{}'".format(a_type))
  if a1 == True:
    raise AssertionError("expected 'a1 == False' but got 'a1 == {}'".format(a1))

## Checks if two objects are the same.
#
#  @param a1
#    Left object to compare.
#  @param a2
#    Right object to compare.
def assertEquals(a1, a2):
  if a1 != a2:
    raise AssertionError("expected '{}' but got '{}'".format(a1, a2))

## Checks if two objects are not the same.
#
#  @param a1
#    Left object to compare.
#  @param a2
#    Right object to compare.
def assertNotEquals(a1, a2):
  if a1 == a2:
    raise AssertionError("expected 'a1 != a2' but got '{} == {}'".format(a1, a2))

## Checks if a result is `None`.
#
#  @param a1
#    Expression result.
def assertNone(a1):
  if a1 != None:
    raise AssertionError("expected 'None' but got '{}'".format(a1))

## Checks if a result is not `None`.
#
#  @param a1
#    Expression result.
def assertNotNone(a1):
  if a1 == None:
    raise AssertionError("expected value but got 'None'")

## Alias for `assertNone`.
assertNull = assertNone
## Alias for `assertNotNone`.
assertNotNull = assertNotNone

## Exception class thrown when an expression was intended to fail.
#
#  @param msg
#    Optional message to display.
class ExpressionSuccessError(AssertionError):
  def __init__(self, msg=None):
    super().__init__(msg)

## Checks that an expression fails.
#
#  @param exp
#    Callable expression.
#  @param args
#    Positional arguments to pass to expression.
#  @param kwargs
#    Keyword arguments to pass to expression.
def assertError(exp, *args, **kwargs):
  exp_string = "{}(".format(exp.__name__)
  arg_list = str(args).strip("(),").split(", ")
  kwarg_string = re.sub(r"'(.*?)': (.*?)[,|}]", r"\1=\2,", str(kwargs)).strip("{},")
  for k in kwarg_string.split(", "):
    arg_list.append(k)
  exp_string += ", ".join(arg_list).rstrip(" ,") + ")"

  try:
    exp(*args, **kwargs)
    raise ExpressionSuccessError("expected error but expression '{}' succeeded".format(exp_string))
  except Exception as e:
    if type(e) in (TypeError, ExpressionSuccessError):
      raise e
