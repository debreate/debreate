
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: docs/LICENSE.txt for details.               *
# ****************************************************

# miscellaneous functions

import hashlib
import importlib
import traceback
import types

from libdbr.logger import getLogger


__logger = getLogger()

## Creates a hash from string or bytes data.
#
#  @param data
#    String or bytes data to process.
#  @return
#    MD5 hex hash string.
def generateMD5Hash(data):
  if type(data) == str:
    data = data.encode()
  tmp = hashlib.md5()
  tmp.update(data)
  return tmp.hexdigest()

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
  except AssertionError:
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
