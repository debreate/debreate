# -*- coding: utf-8 -*-

## \package globals.tooltips
#  
#  Tooltip definitions

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language import GT


# *** Build page *** #
TT_chk_md5 = wx.ToolTip(GT(u'Creates a checksums in the package for all packaged files'))
TT_chk_del = wx.ToolTip(GT(u'Delete staged directory tree after package has been created'))
TT_chk_lint = wx.ToolTip(GT(u'Checks the package for warnings & errors according to lintian\'s specifics\n\
(See: Help -> Reference -> Lintian Tags Explanation)'))
TT_chk_dest = wx.ToolTip(GT(u'Choose the folder where you would like the .deb to be created'))
TT_chk_build = wx.ToolTip(GT(u'Start building'))
