# -*- coding: utf-8 -*-

## \package dbr.help


import wx, os, commands
from wx.richtext import RE_READONLY
from wx.richtext import RichTextCtrl
from globals.bitmaps import BUTTON_HELP


# Local modules
# FIXME: This should use a global manpage file
#app_man = u'{}/man/debreate.1'
app_man = u'man/man1/debreate.1'
local_manpath = u'man'
man_section = u'1'


## Parses & returns Debreate's manpage as RichText
#  
#  \return
#       RichText help reference
def ParseManpage():
    help_text = u'ERROR: Could not parse \'{}\''.format(app_man)
    
    if os.path.isfile(app_man):
        # FIXME: Should text if application is installed on system
        c_man = u'man --manpath={} {} debreate'.format(local_manpath, man_section)
        c_output = commands.getstatusoutput(c_man)
        
        # Command exited successfully
        if not c_output[0]:
            help_text = c_output[1]
    
    return help_text


## TODO: Doxygen
class HelpButton(wx.BitmapButton):
    def __init__(self, parent):
        wx.BitmapButton.__init__(self, parent, wx.ID_HELP, BUTTON_HELP,
                style=wx.NO_BORDER)


## TODO: Doxygen
class HelpDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_HELP, u'Help',
                           style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        dialog_size = wx.Size(200, 200)
        
        self.SetSize(wx.DefaultSize)
        self.SetMinSize(dialog_size)
        
        bg = wx.Panel(self)
        
        help_display = RichTextCtrl(bg, style=RE_READONLY)
        
        sizer_v1 = wx.BoxSizer(wx.VERTICAL)
        sizer_v1.Add(help_display, 1, wx.EXPAND)
        
        bg.SetSizer(sizer_v1)
        bg.SetAutoLayout(True)
        bg.Layout()
