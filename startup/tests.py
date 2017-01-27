# -*- coding: utf-8 -*-

## \package startup.tests
#  
#  Sets list of tests to be checked through app

# MIT licensing
# See: docs/LICENSE.txt


from dbr.log import Logger


## List of available tests
available_tests = (
    u'alpha',
    u'update-fail',
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
#    \b \e String name of test to check for
def UsingTest(test):
    if test not in available_tests:
        Logger.Warn(__name__, u'Requested test not available: {}'.format(test))
    
    return test in test_list
