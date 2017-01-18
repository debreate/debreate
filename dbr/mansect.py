# -*- coding: utf-8 -*-

## \package dbr.mansect

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language       import GT
from dbr.textinput      import TextAreaPanel
from globals.dateinfo   import GetYear


## Base class for manpage parts
class ManBase:
    def __init__(self, parent):
        self.Parent = parent
        
        # Allow adding multiple instances of object
        self.Multiple = False
        
        self.lyt_main = wx.BoxSizer(wx.VERTICAL)
    
    
    ## TODO: Doxygen
    def _add_field(self, label, window, count=1, expand=False):
        if isinstance(label, (unicode, str)):
            label = wx.StaticText(self.Parent, label=label)
        
        lyt_field = wx.BoxSizer(wx.HORIZONTAL)
        
        for X in range(count):
            if expand:
                lyt_field.Add(window, 1, wx.EXPAND)
                continue
            
            lyt_field.Add(window, 1)
        
        self.lyt_main.Add(label, 0, wx.ALIGN_BOTTOM|wx.LEFT, 5)
        
        if expand:
            self.lyt_main.Add(lyt_field, 1, wx.EXPAND|wx.LEFT|wx.BOTTOM, 5)
        
        else:
            self.lyt_main.Add(lyt_field, 1, wx.LEFT|wx.BOTTOM, 5)
        
        self.Parent.Layout()
    
    
    ## Retrieve the main sizer object
    def GetObject(self):
        return self.lyt_main
    
    
    ## Checks multiple instances can be uses
    def MultipleAllowed(self):
        return self.Multiple


## TODO: Doxygen
#  
#  This section is required
#  FIXME: Should derive from wx.Panel/BorderedPanel???
class ManTitle(ManBase):
    def __init__(self, parent):
        ManBase.__init__(self, parent)
        
        txt_name = wx.StaticText(parent, label=GT(u'Name'))
        ti_name = wx.TextCtrl(parent, value=parent.Name)
        
        txt_date = wx.StaticText(parent, label=GT(u'Date'))
        spin_year = wx.SpinCtrl(parent, min=1900, max=2100, initial=GetYear(string_value=False))
        spin_month = wx.SpinCtrl(parent, min=1, max=12)
        spin_day = wx.SpinCtrl(parent, min=1, max=31)
        
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
            (txt_date, 0, wx.LEFT, 5),
            (txt_unknown1, 0, wx.LEFT, 5),
            (txt_unknown2, 0, wx.LEFT, 5),
            (ti_name, 0),
            (lyt_date, 0, wx.LEFT, 5),
            (ti_unknown1, 0, wx.LEFT, 5),
            (ti_unknown2, 0, wx.LEFT, 5),
            ))


## TODO: Doxygen
class ManSectName(ManBase):
    def __init__(self, parent):
        ManBase.__init__(self, parent)
        
        self._add_field(GT(u'Program'), wx.TextCtrl(parent))
        self._add_field(GT(u'Description'), wx.TextCtrl(parent))


## TODO: Doxygen
class ManSectSynopsis(ManBase):
    def __init__(self, parent):
        ManBase.__init__(self, parent)
        
        self._add_field(u'Synopsis', TextAreaPanel(parent), expand=True)
