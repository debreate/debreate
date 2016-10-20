# -*- coding: utf-8 -*-

## \package globals.tooltips
#  
#  Defines tooltips that have longer texts

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.language       import GT
from globals.characters import ARROW_RIGHT
from globals.ident      import ID_BUILD
from globals.ident      import ID_CHANGELOG
from globals.ident      import ID_CONTROL
from globals.ident      import ID_COPYRIGHT
from globals.ident      import ID_DEPENDS
from globals.ident      import ID_FILES
from globals.ident      import ID_MAN
from globals.ident      import ID_MENU
from globals.ident      import ID_SCRIPTS


# *** Wizard buttons ***#
TT_wiz_prev = wx.ToolTip(GT(u'Previous page'))
TT_wiz_next = wx.ToolTip(GT(u'Next page'))

TT_control = {
    u'open': GT(u'Open pre-formatted control text'),
    u'save': GT(u'Save control information to text'),
    u'preview': GT(u'Preview control file'),
    u'package': GT(u'Name that the package will be listed under'),
    u'version': GT(u'Version of release'),
    u'maintainer': GT(u'Name of person who maintains packaging'),
    u'email': GT(u'Package maintainer\'s email address'),
    u'arch': (GT(u'Platform supported by this package/software'), GT(u'all=platform independent'),),
    u'section': GT(u'Section under which package managers will list this package'),
    u'priority': GT(u'Urgency of this package update'),
    u'synopsis': GT(u'Package synopsys'),
    u'description': GT(u'More detailed description'),
    u'source': GT(u'Name of upstream source package'),
    u'homepage': GT(u'Upstream source homepage'),
    u'essential': GT(u'Whether this package is essential to the system'),
}

TT_depends = {
    u'package': GT(u'Package that this depends on'),
    u'version': GT(u'Minimum version that this package supports'),
    u'add': GT(u'Add dependency package to list'),
    u'append': GT(u'Append to selected dependency package in list'),
    u'remove': GT(u'Remove selected dependency package from list'),
    u'clear': GT(u'Clear the list of dependency packages'),
    u'depends': GT(u'Package will need to be installed'),
    u'pre-depends': GT(u'Package will need to be installed and configured first'),
    u'recommends': GT(u'Package is highly recommended and will be installed by default'),
    u'suggests': GT(u'Package may be useful but is not necessary and will not be installed by default'),
    u'enhances': GT(u'This package may be useful to enhanced package'),
    u'conflicts': GT(u'Package will be removed from the system if it is installed'),
    u'replaces': GT(u'Package or its files may be overwritten'),
    u'breaks': GT(u'Package conflicts and will be de-configured'),
    u'list': GT(u'Dependencies to be added'),
}

TT_files = {
    u'add': GT(u'Add selected file/folder'),
    u'remove': GT(u'Remove selected file from list'),
    u'clear': GT(u'Clear file list'),
    u'target': GT(u'Target destination for file(s)'),
    u'browse': GT(u'Browse for target destination'),
    u'refresh': GT(u'Update files\' executable status & availability'),
}

TT_manpages = {
    u'add': GT(u'Add manpage'),
}

TT_scripts = {
    
}

TT_changelog = {
    
}

TT_copyright = {
    
}

TT_launchers = {
    
}

TT_build = {
    
}

# *** Build page *** #

TT_chk_md5 = wx.ToolTip(GT(u'Creates a checksums in the package for all packaged files'))
TT_chk_del = wx.ToolTip(GT(u'Delete staged directory tree after package has been created'))
TT_chk_lint = wx.ToolTip(GT(u'Checks the package for warnings & errors according to lintian\'s specifics\n\
(See: Help {0} Reference {0} Lintian Tags Explanation)').format(ARROW_RIGHT))
TT_chk_dest = wx.ToolTip(GT(u'Choose the folder where you would like the .deb to be created'))


TT_pages = {
    ID_CONTROL: TT_control,
    ID_DEPENDS: TT_depends,
    ID_FILES: TT_files,
    ID_MAN: TT_manpages,
    ID_SCRIPTS: TT_scripts,
    ID_CHANGELOG: TT_changelog,
    ID_COPYRIGHT: TT_copyright,
    ID_MENU: TT_launchers,
    ID_BUILD: TT_build,
}


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


def SetPageToolTips(parent, page_id=None):
    control_list = []
    
    if not page_id:
        page_id = parent.GetId()
    
    # Recursively set tooltips for children
    for C in parent.GetChildren():
        control_list.append(C)
        
        sub_children = C.GetChildren()
        if sub_children:
            SetPageToolTips(C, page_id)
    
    if page_id in TT_pages:
        for C in control_list:
            name = C.GetName().lower()
            
            required = False
            if name and name[-1] == u'*':
                name = name[:-1]
                required = True
            
            if name in TT_pages[page_id]:
                tooltip = TT_pages[page_id][name]
                SetToolTip(tooltip, C, required)
