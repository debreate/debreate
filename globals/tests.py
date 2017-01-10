# -*- coding: utf-8 -*-

## \package globals.tests
#  
#  Sets list of tests to be checked through app

# MIT licensing
# See: docs/LICENSE.txt


## List of available tests
available_tests = (
    u'update',
    )

## List is populated from 'test' command arguments
#  This should be imported by init script
test_list = []

## Get the current list of tests to be run
#  
#  This should be imported form modules other than init script
def GetTestList():
    return test_list
