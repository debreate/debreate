## \package globals.project

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language import GT


# *** Project compression IDs *** #
ID_PROJ_Z = wx.NewId()
ID_PROJ_L = wx.NewId()
ID_PROJ_A = wx.NewId()
ID_PROJ_T = wx.NewId()

## Default project filename extension
PROJECT_ext = "dbpz"

## Legacy project filename extension
PROJECT_ext_legacy = "dbp"
PROJECT_txt_legacy = "txt"

## Filename suffixes that can be opened
supported_suffixes = (
    PROJECT_ext,
    PROJECT_ext_legacy,
    PROJECT_txt_legacy,
    "tar",
    "tar.gz",
    "tar.bz2",
    "tar.xz",
    "zip",
)

PROJ_DEF_Z = GT("Debreate project files")
PROJ_DEF_L = GT("Legacy Debreate project files")
PROJ_DEF_A = GT("All supported formats")
PROJ_DEF_T = GT("Supported compressed archives")

project_wildcards = {
    ID_PROJ_Z: (PROJ_DEF_Z, (supported_suffixes[0],)),
    ID_PROJ_L: (PROJ_DEF_L, (supported_suffixes[1],)),
    ID_PROJ_A: (PROJ_DEF_A, supported_suffixes),
    ID_PROJ_T: (PROJ_DEF_T, supported_suffixes[2:])
}
