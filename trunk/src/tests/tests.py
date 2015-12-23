# -*- coding: utf-8 -*-

# ============================== MIT LICENSE ==================================
#
# Copyright (c) 2015 Jordan Irwin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# =============================================================================

## @package misc
#  Functions for running some tests if TESTING is defined in environment

import os;
from misc.constants import DEBUG, STANDARD_CONFIG;

def ConfigParseTest():
    from config.configparser import ConfigParser;

    parser = ConfigParser();

    def PrintKeyAttempt(key, keytype):
        print('Attempting to retrieve value for {} key "{}"...'.format(keytype, key));

    def GetKeyAttempt(key):
        returnvalue = parser.GetKeyValue(key);

        if (returnvalue):
            print('{}: {}'.format(key, returnvalue));
        else:
            print('Key not found in config file');

    print('Running ConfigParseTest...');

    if (STANDARD_CONFIG):
        print('Checking for config file "{}"...'.format(STANDARD_CONFIG));

        parser.SetConfigFile(STANDARD_CONFIG);

        print('Attempting to load config file...');

        if (parser.LoadConfig()):
            print('Loaded!');

            testkeys = {
                        'VER_MAJ': 'existing',
                        'DUMMY_KEY': 'non-existent',
                        'TEST': 'variable',
                        'VERSION': 'multi-variable',
                        'MIXED': 'invalid-variable'
            };

            for key in testkeys:
                PrintKeyAttempt(key, testkeys[key]);
                GetKeyAttempt(key);

    else:
        print('Variable Error: STANDARD_CONFIG is NULL');

tests = {\
         'ConfigParseTest': ConfigParseTest \
}

def RunTests(testlist):
    print('Running tests...');

    if (testlist):
        for t in testlist:
            tests[t]();
