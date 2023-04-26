
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## Defines tooltips that have longer texts.
#
#  @module globals.tooltips

import wx

import globals.execute

from dbr.language      import GT
from dbr.templates     import local_templates_path
from globals.changes   import section_delims
from libdbr.logger     import Logger
from libdebreate.ident import btnid
from libdebreate.ident import pgid
from ui.helper         import FieldEnabled


_logger = Logger(__name__)

# *** wizard buttons *** #
TT_wiz_prev = wx.ToolTip(GT("Previous page"))
TT_wiz_next = wx.ToolTip(GT("Next page"))

TT_control = {
  "btn browse": GT("Open pre-formatted control text"),
  "btn save": GT("Save control information to text"),
  "btn preview": GT("Preview control file"),
  "package": GT("Name of the package/software"),
  "version": GT("Package/Software release version"),
  "maintainer": GT("Package/Software maintainer's full name"),
  "email": GT("Package/Software maintainer's email address"),
  "architecture": (
    GT("Platform on which package/software is meant to run"), "",
    GT("all = platform independent"),
    ),
  "section": GT("Section under which package managers will list this package"),
  "priority": GT("Urgency of this package update"),
  "synopsis": GT("One line descriptions/synopsis"),
  "description": (
    GT("More detailed description"), "",
    GT("Multiple lines can be used here, but lintian will complain if they are too long")
    ),
  "source": GT("Name of upstream source package"),
  "homepage": GT("Upstream source homepage URL"),
  "essential": GT("Whether this package is essential for system's stability"),
}

TT_depends = {
  "btn browse": TT_control["btn browse"],
  "btn save": TT_control["btn save"],
  "btn preview": TT_control["btn preview"],
  "package": GT("Name of dependency/conflicting package"),
  "operator": GT("Operator"),
  "version": GT("Version corresponding to package name and operator"),
  "depends": GT("Package will need to be installed"),
  "pre-depends": GT("Package will need to be installed and configured first"),
  "recommends": GT("Package is highly recommended and will be installed by default"),
  "suggests": GT("Package may be useful but is not necessary and will not be installed by default"),
  "enhances": GT("This package may be useful to enhanced package"),
  "conflicts": GT("Package will be removed from the system if it is installed"),
  "replaces": GT("Package or its files may be overwritten"),
  "breaks": GT("Package conflicts and will be de-configured"),
  "btn add": GT("Add dependency package to list"),
  "btn append": GT("Add as alternative to selected dependency packages in list"),
  "btn remove": GT("Remove selected dependency package from list"),
  "btn clear": GT("Clear the list of dependency packages"),
  "list": GT("Dependencies to be added"),
}

TT_files = {
  "individually": GT("Files from selected directories will be added individually to list"),
  "btn add": GT("Add selected file/folder to list"),
  "btn remove": GT("Remove selected files from list"),
  "btn clear": GT("Clear file list"),
  "btn browse": GT("Browse for target installation directory"),
  "btn refresh": GT("Update files' executable status & availability"),
  "target": GT("Target installation directory for file(s)"),
  "filelist": (
      GT("Files to be added to package & their target directories"), "",
      GT("Blue text = directory"),
      GT("Red text = executable"),
      GT("Red background = missing file/directory"),
      )
}

TT_manpages = {
  "add": GT("Add manpage"),
}

TT_scripts = {
  "preinst": GT("Script run before package install begins"),
  "postinst": GT("Scrtipt run after package install completes"),
  "prerm": GT("Script run before package uninstall begins"),
  "postrm": GT("Script run after package uninstall completes"),
  "script body": GT("Script text body"),
  "target": GT("Directory where scripts should create symlinks"),
  "al list": GT("Executables from file list to be linked against"),
  "btn import": GT("Import files marked as executable from Files page"),
  "btn remove": GT("Remove selected executables from list"),
  "btn build": GT("Generate scripts"),
  "btn help": GT("How to use Auto-Link"),
}

TT_changelog = {
  "package": TT_control["package"],
  "version": TT_control["version"],
  "dist": (
    GT("Name of Debian/Ubuntu/etc. target distribution"), "",
    GT("See \"Options ➜ Update dist names cache\" to update this list.")
    ),
  "urgency": TT_control["priority"],
  "maintainer": TT_control["maintainer"],
  "email": TT_control["email"],
  "changes": (
    GT("List new changes here, separated one per line"), "",
    GT("The first line will be prepended with an asterix (*) automatically. To denote any other sections, put one of the following as the first character on the line:"),
    "\t{}".format(",  ".join(list(section_delims))),
    ),
  "target default": GT("Install changelog to standard directory"),
  "target custom": GT("Install changelog to custom directory"),
  "btn import": GT("Import information from Control page"),
  "btn add": GT("Prepend above changes as new log entry"),
  "indent": GT("Do not strip preceding whitespace from regular lines"),
  "log": GT("Formatted changelog entries (editable)"),
}

no_lic_templates = GT("No license templates available")
TT_copyright = {
  "list_disabled": no_lic_templates,
  "full": (
    GT("Full Template"), "",
    GT("Copies a full system, app, or local license"),
    GT("SYSTEM:"), "\t{}".format(GT("Copies text from a license stored in")),
    "\t/usr/share/common-licenses",
    GT("APP:"), "\t{}".format(GT("Copies a template distributed with Debreate")),
    GT("LOCAL:"), "\t{}".format(GT("Copies a user-defined template from")),
    "\t{}".format(local_templates_path),
    ),
  "full_disabled": no_lic_templates,
  "short": (
    GT("Short Template"), "",
    GT("Creates a copyright header & short reference to a standard system license in /usr/share/common-licenses"),
    ),
  "short_disabled": no_lic_templates,
}

TT_menu = {
  "open": GT("Import launcher from file"),
  "export": GT("Export launcher to text file"),
  "preview": GT("Preview launcher text"),
  "filename": GT("Custom filename to use for launcher"),
  "filename chk": GT("Unless checked, the value of \"Filename\" will be used for the launcher's output filename"),
  "name": GT("Name to be displayed for the launcher"),
  "exec": GT("Executable to be launched"),
  "comment": GT("Text displayed when cursor hovers over launcher"),
  "icon": GT("Icon to be displayed for the launcher"),
  "type": (
    GT("Type of launcher"), "",
    GT("Application:"), "\t{}".format(GT("Shortcut to an application")),
    GT("Link:"), "\t{}".format(GT("Shortcut to a web URL")),
    GT("Directory:"), "\t{}".format(GT("Container of meta data of a menu entry")),
    ),
  "terminal": GT("Specifies whether application should be run in a terminal"),
  "startupnotify": GT("Displays a notification in the system panel when launched"),
  "encoding": GT("Sets the encoding that should be used to read the launcher"),
  "category": GT("Categories dictate where the launcher will be located in the system menu"),
  "add category": GT("Append current category to list"),
  "rm category": GT("Remove selected categories from list"),
  "clear categories": GT("Clear category list"),
  "categories": GT("Categories dictate where the launcher will be located in the system menu"),
  "no disp": GT("This options means \"This application exists, but don't display it in the menus\""),
  "show in": GT("Launcher is only shown when options are satisfied"),
  "other": (
    GT("Miscellaneous fields not available above"), "",
    GT("See \"Help ➜ Reference ➜ Launchers / Desktop Entries\" for more available options"), "",
    GT("Warning:"),
    "\t{}".format(GT("Improperly formatted text may cause launcher to be unusable")),
    )
}

TT_build = {
  "md5": GT("Creates a checksum for all staged files within the package"),
  "md5_disabled": GT("Install md5sum package for this option"),
  "permiss": GT("Ensure files & directories use standard permissions"),
  "strip": (
    GT("Discards unneeded symbols from binary files"), "",
    GT("See \"man 1 strip\""),
    ),
  "strip_disabled": GT("Install binutils package for this option"),
  "rmstage": GT("Delete staged directory tree after package has been created"),
  "lintian": (
    GT("Checks the package for warnings & errors according to lintian specifications"), "",
    GT("See \"Help ➜ Reference ➜ Lintian Tags Explanation\""),
    ),
  "lintian_disabled": GT("Install lintian package for this option"),
  btnid.BUILD: GT("Start building"),
  "install": (
    GT("Install package using a system installer after build"), "",
    "{} {}".format(GT("System installer set to:"), globals.execute.getDebInstaller()),
    ),
  "install_disabled": (
    GT("Installation requires one of the following utilities:"), "",
    GT("gdebi-gtk, gdebi-kde"),
    ),
}


TT_pages = {
  pgid.CONTROL: TT_control,
  pgid.DEPENDS: TT_depends,
  pgid.FILES: TT_files,
  pgid.MAN: TT_manpages,
  pgid.SCRIPTS: TT_scripts,
  pgid.CHANGELOG: TT_changelog,
  pgid.COPYRIGHT: TT_copyright,
  pgid.MENU: TT_menu,
  pgid.BUILD: TT_build,
}


## Universal function for setting window/control tooltips.
def SetToolTip(tooltip, control, required=False):
  if isinstance(tooltip, wx.ToolTip):
    tooltip = tooltip.GetTip()
  elif isinstance(tooltip, (tuple, list)):
    tooltip = "\n".join(tooltip)

  if tooltip:
    if required:
      tooltip = "{}\n\n{}".format(tooltip, GT("Required"))
    register(control, tooltip)


## Sets multiple tooltips at once.
def SetToolTips(tooltip, control_list, required=False):
  for FIELD in control_list:
    SetToolTip(tooltip, FIELD, required)


## @todo Doxygen
def SetPageToolTips(parent, page_id=None):
  control_list = []

  if not page_id:
    page_id = parent.GetId()

  # recursively set tooltips for children
  for FIELD in parent.GetChildren():
    control_list.append(FIELD)

    sub_children = FIELD.GetChildren()
    if sub_children:
      SetPageToolTips(FIELD, page_id)

  if page_id in TT_pages:
    for FIELD in control_list:
      tooltip = None

      # use ID first
      field_id = FIELD.GetId()
      if field_id in TT_pages[page_id]:
        tooltip = TT_pages[page_id][field_id]

      else:
        try:
          name = str(FIELD.tt_name).lower()

        except AttributeError:
          try:
            name = FIELD.GetName().lower()

          except AttributeError:
            _logger.warn("Object has no name, not setting tooltip: {}".format(type(FIELD)))

            continue

        required = False
        if name:
          if "*" in name[-2:]:
            required = True

          # the » character causes a different tooltip to be set for disabled fields
          if "»" in name[-2:] and not FieldEnabled(FIELD):
            name = "{}_disabled".format(name)

          name = name.replace("*", "")
          name = name.replace("»", "")

        if name in TT_pages[page_id]:
          tooltip = TT_pages[page_id][name]

      if tooltip:
        SetToolTip(tooltip, FIELD, required)


__registry = {}
__enabled = False

## Registers a tooltip associated with a window.
#
#  @param window
#    `wx.Window` instance.
#  @param tt
#    Text to display for tooltip.
def register(window, tt):
  if isinstance(tt, wx.ToolTip):
    tt = tt.GetTip()
  __registry[window] = tt
  if __enabled:
    window.SetToolTip(wx.ToolTip(tt))

## Unregisters a window's tooltip.
#
#  @param window
#    `wx.Window` instance to be unregistered.
def unregister(window):
  if window in __registry:
    del __registry[window]

## Enables or disables tooltips globally.
#
#  @param enabled
#    Flag dertimining if tooltips should be enabled or disabled.
def enable(enabled=True):
  global __enabled
  __enabled = enabled
  wx.ToolTip.Enable(enabled)
  if __checkEnabled() == enabled:
    return True
  # fallback to manually setting
  _logger.debug("registered tooltips: {}".format(len(__registry)))
  for window in tuple(__registry):
    if not window:
      _logger.debug("element deleted: {}".format(window))
      del __registry[window]
      continue
    if enabled:
      window.SetToolTip(wx.ToolTip(__registry[window]))
    else:
      window.UnsetToolTip()
  _logger.debug("tooltip state 'enabled={}' set manually".format(enabled))
  return __checkEnabled() == enabled

## Gets the cached state.
#
#  @return
#    `True` if state is enabled.
def areEnabled():
  return __enabled

## Checks registered windows for enabled tooltips.
#
#  Note: Requires at least one tooltip to be registered.
#
#  @return
#    `True` if global tooltips are recognized as enabled.
def __checkEnabled():
  for window in tuple(__registry):
    if not window:
      _logger.debug("element deleted: {}".format(window))
      del __registry[window]
      continue
    if window.GetToolTip() != None:
      return True
  return False
