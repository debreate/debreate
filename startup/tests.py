
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module startup.tests
#
#  Sets list of tests to be checked through app

from libdbr.logger import Logger


logger = Logger(__name__)

## List of available tests
available_tests = (
  "alpha",
  "update-fail",
  )

## List is populated from 'test' command arguments
#  This should be imported by init script
test_list = []

## Get the current list of tests to be run
#
#  This should be imported form modules other than init script
def GetTestList():
  return test_list


## Check if a test is currently in use
#
#  \param test
#  \b \e String name of test to check for
def UsingTest(test):
  if test not in available_tests:
    logger.warn("Requested test not available: {}".format(test))

  return test in test_list
