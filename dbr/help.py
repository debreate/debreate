# -*- coding: utf-8 -*-

## \package dbr.help


# System modules
import wx, os, commands

# Local modules
from dbr.constants import ID_HELP


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


class HelpDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, ID_HELP, u'Help')
