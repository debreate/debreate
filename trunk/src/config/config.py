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
#  Manages configuration files

import os;

from constants import DATADIR, INSTALLED;

class Config():
    def __init__(self, name=None):
        self.name = name;
        self.configfile = '{}/data/config'.format(DATADIR);
        if (not INSTALLED):
            self.configfile = os.path.dirname(DATADIR) + '/data/config';
        self.configdata = {};

        # Fill configuration data on initialization
        self.LoadConfigData();

    ## Get a value defined in the config file
    #
    def GetValue(self, key):
        if (self.configdata):
            try:
                value = self.configdata[key];
            except KeyError:
                return(None);

#            # Values with expandable variables
#            if (('{' in value) or ('<' in value)):
#                value = self.ExpandVariables(value);
#
#            # List values
#            if ((';' in value) or (',' in value)):
#                value = self.ParseList(value);

            # Return value without any modifications (plain variables)
            return(value);

        return(None);

    def ExpandVariables(self, value):
        def ReplaceVarNames(value, ldelim, rdelim):
            varcount = 0;
            while (ldelim in value):
                if (rdelim not in value):
                    break;
                start = value.index(ldelim);
                end = value.index(rdelim);
                var = value[start + 1:end];
                if (ldelim == '{'):
                    replacement = os.getenv(var);
                else:
                    replacement = self.GetValue(var);
                value = value.replace(''.join((ldelim, var, rdelim)), replacement);
                varcount += 1;

            return(varcount, value);

        varcount = 0;
        changes = ReplaceVarNames(value, '{', '}');
        varcount += changes[0];
        if (varcount):
            value = changes[1];

        changes = ReplaceVarNames(value, '<', '>');
        varcount += changes[0];
        if (varcount):
            value = changes[1];

        if (varcount):
            return(value);

        return(None);

    ## Separate value elements into a list
    #
    def ParseList(self, value):
        vlist = ','.join(value.split(';')).split(',');

        index = len(vlist) - 1;
        while (index >= 0):
            # Remove any empty objects
            if (not ''.join(vlist[index].split(' '))):
                del vlist[index];
            index -= 1;

        return(vlist);

    ## Initalize the configuration information in key=value format
    #
    def LoadConfigData(self):
        # Start with empty config
        self.configdata = {};

        # Open file for reading
        if (os.path.isfile(self.configfile)):
            cfile = open(self.configfile, 'r+t');
            if (cfile):
                lines = cfile.read().split('\n');
                for l in lines:
                    # Only get lines that begin with alphabetic characters
                    if (l[0].isalpha()):
                        # Load lines that use key=value layout
                        if ('=' in l):
                            key = l.split('=')[0];
                            value = l.split('=')[1];

                            # Values with expandable variables
                            if (('{' in value) or ('<' in value)):
                                value = self.ExpandVariables(value);

                            # List values
                            if ((';' in value) or (',' in value)):
                                value = self.ParseList(value);

                            self.configdata[key] = value;

        # Config loaded successfully
        if (self.configdata):
            return(True);

        return(False);

    def SetName(self, name):
        self.name = name;

    def GetName(self):
        return(self.name);


configuration = Config('Debreate Main Config');
