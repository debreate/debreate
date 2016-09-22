# -*- coding: utf-8 -*-

import wx

from dbr.constants import ID_MAN


class Panel(wx.Panel):
    def __init__(self, parent):
        # FIXME: Add to Gettext locale files
        wx.Panel.__init__(self, parent, ID_MAN, name=_(u'Manpages'))
        
        self.parent = parent
