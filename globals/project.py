# -*- coding: utf-8 -*-

## \package globals.project

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language import GT


ID_PROJ_L = wx.NewId()
ID_PROJ_T = wx.NewId()
ID_PROJ_M = wx.NewId()

## Default project filename extension
PROJECT_ext = u'dbp'
PROJECT_txt = u'txt'

## Filename suffixes that can be opened
supported_suffixes = (
    PROJECT_ext,
    PROJECT_txt,
)

PROJ_DEF_L = GT(u'Debreate project files')

project_wildcards = {
    ID_PROJ_L: (PROJ_DEF_L, (PROJECT_ext, PROJECT_txt)),
}
