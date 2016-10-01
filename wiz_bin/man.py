# -*- coding: utf-8 -*-

import wx

from dbr.language import GT
from dbr.constants import ID_MAN


class Panel(wx.Panel):
    def __init__(self, parent):
        # TODO: Add to Gettext locale files
        wx.Panel.__init__(self, parent, ID_MAN, name=GT(u'Manpages'))
        
        self.parent = parent
    
    
    ## Retrieves manpages info for text output
    #  
    #  TODO: Nothing here yet
    def GetPageInfo(self):
        return wx.EmptyString
