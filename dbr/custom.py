# -*- coding: utf-8 -*-

## \package dbr.custom

# MIT licensing
# See: docs/LICENSE.txt


import sys, wx

from ui.textinput import TextAreaPanel


## A generic display area that captures \e stdout & \e stderr
class OutputLog(TextAreaPanel):
    def __init__(self, parent):
        TextAreaPanel.__init__(self, parent, style=wx.TE_READONLY)
        self.stdout = sys.stdout
        self.stderr = sys.stderr
    
    
    ## Adds test to the display area
    def write(self, string):
        self.AppendText(string)
    
    
    ## TODO: Doxygen
    def ToggleOutput(self, event=None):
        if sys.stdout == self:
            sys.stdout = self.stdout
            sys.stderr = self.stderr
        
        else:
            sys.stdout = self
            sys.stdout = self
