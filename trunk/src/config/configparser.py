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

## @package config
#  Configuration parser that retrieves key=value entries

import os;

class ConfigParser():
    def __init__(self):
        self.configfile = None;
        self.configdata = {};

    def ConfigExists(self):
        return(os.path.isfile(self.configfile));

    def ExpandVariables(self, value):
        returnvalue = value;

        foundvariables = {};
        for v in value.split('${'):
            if ('}' in v):
                key = v.split('}')[0];
                val = self.GetKeyValue(key);

                if (val):
                    foundvariables[key] = val;
                    returnvalue = returnvalue.replace('${%s}' % key, val);

        if (foundvariables):
            return(returnvalue);

        return(None);

    def GetConfigFile(self):
        return(self.configfile);

    def GetKeyValue(self, key):
        try:
            value = self.configdata[key];
        except KeyError:
            return None;

        if ('${' in value and '}' in value):
            expandedvalues = self.ExpandVariables(value);
            return(expandedvalues);

        return(self.configdata[key]);

    def LoadConfig(self):
        openfile = open(self.configfile, 'r+t');
        if (openfile):
            for line in openfile.read().split('\n'):
                if (line[0].isalpha()):
                    # FIXME:
                    print('First char is alpha');

                    if ('=' in line):
                        key = line.split('=')[0];
                        value = line.split('=')[1];
                        self.configdata[key] = value;

            openfile.close();

            if (self.configdata):
                ## Make sure configuration data isn't empty #
                return True;

        return False;

    def SetConfigFile(self, filename):
        self.configfile = filename;
