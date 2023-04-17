
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## Sets list of tests to be checked through app.
#
#  @module startup.tests

from libdbr.logger  import Logger
from libdbr.strings import sgr


__logger = Logger(__name__)

## List of available tests.
__available = {
  "alpha": "Enables features not ready for stable release.",
  "update-fail": "Forces update check to fail."
}

## Active tests enabled with --test from the command line.
__active = []

## Checks if a test is active.
#
#  @param _id
#    String test identifier.
#  @return
#    `True` if id is in active list.
def isActive(_id):
  if _id not in __available:
    __logger.warn("requested test ID '{}' not available".format(_id))
  return _id in __active

## Activates a test.
#
#  @param _id
#    String test identifier.
def activate(_id):
  if _id not in __available:
    raise TypeError(sgr("unknown test ID '<bold>{}</bold>'".format(_id)))
  if _id in __active:
    __logger.warn("test ID '{}' already active".format(_id))
    return
  __active.append(_id)
