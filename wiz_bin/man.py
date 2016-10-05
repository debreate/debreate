# -*- coding: utf-8 -*-

import wx

from dbr.language import GT
from dbr.constants import ID_MAN
from dbr.wizard import WizardPage


class Panel(WizardPage):
    def __init__(self, parent):
        # TODO: Add to Gettext locale files
        WizardPage.__init__(self, parent, ID_MAN)
        
        self.parent = parent
    
    
    ## Retrieves manpages info for text output
    #  
    #  TODO: Nothing here yet
    def GetPageInfo(self):
        return wx.EmptyString
