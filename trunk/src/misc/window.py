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

##
# This script is the base of the application. It defines the user interface
# and executes workload after the interface has been created.

from constants import REQ_WXVER;

import wxversion;
wxversion.select(REQ_WXVER);

# System imports
import wx;

# Local imports
from wizard import WizardLayout;
from panel.info import InfoPanel;

##
# The main user interface class
class MainWindow(wx.Frame):
    def __init__(self, title, size=(800, 600)):
        super(MainWindow, self).__init__(None, title=title, size=size);

        self.SetMinSize((640, 400))

        # Create a wizard-style layout
        wizard = WizardLayout(self);

