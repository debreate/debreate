# -*- coding: utf-8 -*-

## \package globals.tooltips
#  
#  Defines tooltips that have longer texts

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language       import GT
from globals.characters import ARROW_RIGHT


## Universal function for setting window/control tooltips
def SetToolTip(tooltip, control, required=False):
    if isinstance(tooltip, wx.ToolTip):
        tooltip = tooltip.GetTip()
    
    elif isinstance(tooltip, (tuple, list)):
        tooltip = u'\n'.join(tooltip)
    
    if tooltip:
        if required:
            tooltip = u'{}\n\n{}'.format(tooltip, GT(u'Required'))
        
        control.SetToolTipString(tooltip)


## Sets multiple tooltips at once
def SetToolTips(tooltip, control_list, required=False):
    for C in control_list:
        SetToolTip(tooltip, C, required)


# *** Wizard buttons ***#

TT_wiz_prev = wx.ToolTip(GT(u'Previous page'))
TT_wiz_next = wx.ToolTip(GT(u'Next page'))

# *** Control page *** #
TT_control_btn = {
    u'browse': GT(u'Open pre-formatted control text'),
    u'save': GT(u'Save control information to text'),
    u'preview': GT(u'Preview control file'),
}

TT_control_input = {
    u'package': GT(u'Name that the package will be listed under'),
    u'version': GT(u'Version of release'),
    u'maint': GT(u'Name of person who maintains packaging'),
    u'email': GT(u'Package maintainer\'s email address'),
    u'arch': (GT(u'Platform supported by this package/software'), GT(u'all=platform independent'),),
    u'section': GT(u'Section under which package managers will list this package'),
    u'priority': GT(u'Urgency of this package update'),
    u'desc-short': GT(u'Package synopsys'),
    u'desc-long': GT(u'More detailed description'),
    u'source': GT(u'Name of upstream source package'),
    u'homepage': GT(u'Upstream source homepage'),
    u'essential': GT(u'Whether this package is essential to the system'),
}

# *** Files page *** #
TT_files_refresh = wx.ToolTip(GT(u'Update files\' executable status & availability'))

# *** Build page *** #

TT_chk_md5 = wx.ToolTip(GT(u'Creates a checksums in the package for all packaged files'))
TT_chk_del = wx.ToolTip(GT(u'Delete staged directory tree after package has been created'))
TT_chk_lint = wx.ToolTip(GT(u'Checks the package for warnings & errors according to lintian\'s specifics\n\
(See: Help {0} Reference {0} Lintian Tags Explanation)').format(ARROW_RIGHT))
TT_chk_dest = wx.ToolTip(GT(u'Choose the folder where you would like the .deb to be created'))
