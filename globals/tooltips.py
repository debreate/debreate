# -*- coding: utf-8 -*-

## \package globals.tooltips
#  
#  Defines tooltips that have longer texts

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.functions      import FieldEnabled
from dbr.language       import GT
from dbr.templates      import local_templates_path
from globals.characters import ARROW_RIGHT
from globals.commands   import CMD_gdebi_gui
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
    u'preinst': GT(u'Script run before package install begins'),
    u'postinst': GT(u'Scrtipt run after package install completes'),
    u'prerm': GT(u'Script run before package uninstall begins'),
    u'postrm': GT(u'Script run after package uninstall completes'),
    u'target': GT(u'FIXME: Description???'),
    u'import': GT(u'Import files marked as executable from Files page into Auto-Link list'),
    u'remove': GT(u'Remove the selected executable from the Auto-Link list'),
    u'generate': GT(u'Generate Scripts'),
    u'help': GT(u'How to use Auto-Link'),
}

TT_changelog = {
    u'package': TT_control[u'package'],
    u'version': TT_control[u'version'],
    u'dist': GT(u'Name of Debian/Ubuntu/etc. target distribution'),
    u'urgency': GT(u'Update urgency'),
    u'maintainer': TT_control[u'maintainer'],
    u'email': TT_control[u'email'],
    u'changes': GT(u'List new changes here, separated one per line'),
    u'target': GT(u'Target to install changelog file'),
    u'import': GT(u'Import information from Control section'),
    u'add': GT(u'Prepend above changes as new log entry'),
    u'log': GT(u'Log contents'),
}

TT_copyright = {
    u'full': (
        u'{}\n'.format(GT(u'Copies a full system, app, or local license')),
        GT(u'SYSTEM:'), u'\t{}'.format(GT(u'Copies text from a license stored in')),
        u'\t/usr/share/common-licenses',
        GT(u'APP:'), u'\t{}'.format(GT(u'Copies a template distributed with Debreate')),
        GT(u'LOCAL:'), u'\t{}'.format(GT(u'Copies a user-defined template from')),
        u'\t{}'.format(local_templates_path),
        ),
    u'link': GT(u'Creates a copyright header & short reference to a standard license in /usr/share/common-licenses'),
}

TT_menu = {
    u'open': GT(u'Import launcher from file'),
    u'export': GT(u'Export launcher to text file'),
    u'preview': GT(u'Preview launcher text'),
    u'filename': GT(u'Custom filename to use for launcher'),
    u'filename chk': GT(u'Unless checked, the value of "Filename" will be used for the launcher\'s output filename'),
    u'name': GT(u'Name to be displayed for the launcher'),
    u'exec': GT(u'Executable to be launched'),
    u'comment': GT(u'Text displayed when cursor hovers over launcher'),
    u'icon': GT(u'Icon to be displayed for the launcher'),
    u'type': (
        GT(u'Type of launcher'), u'',
        GT(u'Application:'), u'\t{}'.format(GT(u'Shortcut to an application')),
        GT(u'Link:'), u'\t{}'.format(GT(u'Shortcut to a web URL')),
        GT(u'Directory:'), u'\t{}'.format(GT(u'Container of meta data of a menu entry')),
        ),
    u'terminal': GT(u'Specifies whether application should be run in a terminal'),
    u'startupnotify': GT(u'Displays a notification in the system panel when launched'),
    u'encoding': GT(u'Sets the encoding that should be used to read the launcher'),
    u'category': GT(u'Categories dictate where the launcher will be located in the system menu'),
    u'add category': GT(u'Append current category to list'),
    u'rm category': GT(u'Remove selected categories from list'),
    u'clear categories': GT(u'Clear category list'),
    u'categories': GT(u'Categories dictate where the launcher will be located in the system menu'),
    u'no disp': GT(u'This options means "This application exists, but don\'t display it in the menus"'),
    u'show in': GT(u'Launcher is only shown when options are satisfied'),
    u'other': (
        GT(u'Miscellaneous fields not available above'), u'',
        GT(u'See "Help ➜ Reference ➜ Launchers / Dekstop Entries" for more available options'), u'',
        GT(u'Warning:'),
        u'\t{}'.format(GT(u'Improperly formatted text may cause launcher to be unusable')),
        )
}

TT_build = {
    u'md5': GT(u'Creates a checksum for all staged files within the package'),
    u'md5_disabled': GT(u'Install md5sum package for this option'),
    u'rmstage': GT(u'Delete staged directory tree after package has been created'),
    u'lintian': (
        GT(u'Checks the package for warnings & errors according to lintian specifications'), u'',
        GT(u'See: Help {0} Reference {0} Lintian Tags Explanation').format(ARROW_RIGHT),
        ),
    u'lintian_disabled': GT(u'Install lintian package for this option'),
    u'build': GT(u'Start building'),
    u'install': (
        GT(u'Install package using a system installer after build'), u'',
        u'{} {}'.format(GT(u'System installer set to:'), CMD_gdebi_gui),
        ),
    u'install_disabled': (
        GT(u'Installation requires one of the following utilities:'), u'',
        GT(u'gdebi-gtk, gdebi-kde'),
        ),
}


TT_pages = {
    ID_CONTROL: TT_control,
    ID_DEPENDS: TT_depends,
    ID_FILES: TT_files,
    ID_MAN: TT_manpages,
    ID_SCRIPTS: TT_scripts,
    ID_CHANGELOG: TT_changelog,
    ID_COPYRIGHT: TT_copyright,
    ID_MENU: TT_menu,
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
            try:
                name = C.tt_name.lower()
            except AttributeError:
                name = C.GetName().lower()
            
            required = False
            if name:
                if u'*' in name[-2:]:
                    #name = name[:name.index(u'*')]
                    required = True
                
                # The » character causes a different tooltip to be set for disabled fields
                if u'»' in name[-2:] and not FieldEnabled(C):
                    name = u'{}_disabled'.format(name)
                
                name = name.replace(u'*', u'')
                name = name.replace(u'»', u'')
            
            if name in TT_pages[page_id]:
                tooltip = TT_pages[page_id][name]
                SetToolTip(tooltip, C, required)
