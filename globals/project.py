# -*- coding: utf-8 -*-

## \package globals.project

# MIT licensing; See: docs/LICENSE.txt


# System modules
import wx

# Local modules
from dbr.language import GT


ID_PROJ_L = wx.NewId()

## Default project filename extension
PROJECT_ext = u'dbp'

## Filename suffixes that can be opened
supported_suffixes = (
    u'dbp',
)

PROJ_DEF_L = GT(u'Debreate projects')

project_wildcards = {
    ID_PROJ_L: (PROJ_DEF_L, (supported_suffixes[0],)),
}
