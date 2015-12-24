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

## @package debug
#

# System modules
from sys import stdout, stderr;

def Message(message, level='DEBUG', script=None, line=None):
    # Console text output
    ANSI_DEFAULT = '\033[0m';
    ANSI_GREEN = '\033[0;32m';
    ANSI_GREEN_I = ANSI_GREEN.replace('[0;', '[3;');
    ANSI_BLUE = '\033[0;34m';
    ANSI_BLUE_I = ANSI_BLUE.replace('[0;', '[3;');
    ANSI_YELLOW = '\033[0;33m';
    ANSI_YELLOW_I = ANSI_YELLOW.replace('[0;', '[3;');
    ANSI_RED = '\033[0;31m';
    ANSI_RED_I = ANSI_RED.replace('[0;', '[3;');

    levels = {'DEBUG': ANSI_GREEN_I, 'INFO': ANSI_BLUE_I,
              'WARN': ANSI_YELLOW_I, 'ERROR': ANSI_RED_I
    };
    level = level.upper();
    write = stderr.write;

    if (level in levels):
        prefix = '{}:'.format(level);
        if (script):
            if (line):
                script = '{}, {}'.format(script, line);
            prefix = '{} ({}):'.format(level, script);

        if (level == 'INFO'):
            write = stdout.write;

        write(levels[level] + '{} {}'.format(prefix, message) + ANSI_DEFAULT + '\n');
    else:
        write(levels['ERROR'] + 'ERROR: Debug level \'{}\' not available.'.format(level) + ANSI_DEFAULT + '\n');
