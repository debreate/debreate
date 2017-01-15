# -*- coding: utf-8 -*-

## \package dbr.mansect

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language import GT


## Base class for manpage parts
class ManBase:
    def __init__(self, parent):
        self.lyt_main = wx.Sizer
    
    
    ## Retrieve the main sizer object
    def GetObject(self):
        return self.lyt_main


## TODO: Doxygen
#  
#  This section is required
#  FIXME: Should derive from wx.Panel/BorderedPanel???
class ManTitle(ManBase):
    def __init__(self, parent):
        ManBase.__init__(self, parent)
        
        txt_name = wx.StaticText(parent, label=GT(u'Name'))
        ti_name = wx.TextCtrl(parent)
        
        txt_section = wx.StaticText(parent, label=GT(u'Section'))
        # TODO: Add section & descriptions
        sel_section = wx.Choice(parent)
        
        txt_date = wx.StaticText(parent, label=GT(u'Date'))
        spin_year = wx.SpinCtrl(parent)
        spin_month = wx.SpinCtrl(parent)
        spin_day = wx.SpinCtrl(parent)
        
        # FIXME: What is this for?
        txt_unknown1 = wx.StaticText(parent, label=GT(u'Unknown'))
        ti_unknown1 = wx.TextCtrl(parent)
        
        # FIXME: What is this for?
        txt_unknown2 = wx.StaticText(parent, label=GT(u'Unknown'))
        ti_unknown2 = wx.TextCtrl(parent)
        
        # *** Layout *** #
        
        lyt_date = wx.BoxSizer(wx.HORIZONTAL)
        lyt_date.AddMany((
            spin_year,
            spin_month,
            spin_day,
            ))
        
        self.lyt_main = wx.FlexGridSizer(rows=2)
        self.lyt_main.AddMany((
            txt_name,
            txt_section,
            txt_date,
            txt_unknown1,
            txt_unknown2,
            ti_name,
            sel_section,
            lyt_date,
            ti_unknown1,
            ti_unknown2,
            ))
