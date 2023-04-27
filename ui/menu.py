
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module ui.menu

import wx

import dbr.config

from dbr.config        import ConfCode
from dbr.config        import GetDefaultConfigValue
from dbr.language      import GT
from globals.bitmaps   import ICON_CLOCK
from globals.bitmaps   import ICON_GLOBE
from globals.bitmaps   import ICON_LOGO
from libdbr            import config
from libdbr            import paths
from libdbr.logger     import Logger
from libdebreate.ident import menuid
from libdebreate.ident import refid
from startup           import tests


logger = Logger(__name__)

## A menu bar that stores an ID along with a menu.
class MenuBar(wx.MenuBar):
  ## Constructor
  #
  #  @param parent
  #    <b><i>wx.Window</i></b> parent window of the menu bar. If not None, automatically sets itself
  #    as parent's menu bar.
  #  @param style
  #    Menu bar style represented by an <b><i>integer</i></b> value.
  def __init__(self, parent=None, style=0):
    wx.MenuBar.__init__(self, style)
    self.id_list = []
    if isinstance(parent, wx.Frame):
      parent.SetMenuBar(self)

  ## Append a menu to the end of menu bar
  #
  #  @param menu
  #    <b><i>wx.Menu</i></b> instance to be appended
  #  @param title
  #    Label to be displayed in the menu bar
  #  @param menuId
  #    Unique <b><i>integer</i></b> identifier to store for menu
  def Append(self, menu, title, menuId):
    self.id_list.append(menuId)
    return wx.MenuBar.Append(self, menu, title)

  ## Finds a wx.Menu by ID
  #
  #  @param menuId
  #    Menu <b><i>integer</i></b> identifier to search for in menu bar
  #  @return
  #    The <b><i>wx.Menu</i></b> with using identifier
  def GetMenuById(self, menuId):
    m_index = self.id_list.index(menuId)
    return self.GetMenu(m_index)

  ## Insert a menu to a specified position in the menu bar
  #
  #  @param index
  #    Position index to insert menu
  #  @param menu
  #    <b><i>wx.Menu</i></b> instance to be inserted
  #  @param title
  #    Label to be displayed in the menu bar
  #  @param menuId
  #    Unique <b><i>integer</i></b> identifier to store for menu
  def Insert(self, index, menu, title, menuId):
    self.id_list.insert(index, menuId)
    return wx.MenuBar.Insert(self, index, menu, title)


## Creates the main menu bar.
#
#  @param parent
#    Main wx.Frame window
#  @return
#    New MenuBar instance
def createMenuBar(parent):
  testing = tests.isActive("alpha") or logger.debugging()

  menubar = MenuBar(parent)

  menu_file = wx.Menu()

  menubar.Append(menu_file, GT("File"), menuid.FILE)
  # This menu is filled from ui.wizard.Wizard.SetPages
  menubar.Append(wx.Menu(), GT("Page"), menuid.PAGE)

  # *** File Menu *** #

  mitems_file = [
    (menuid.NEW, GT("New project"), GT("Start a new project"),),
    (menuid.OPEN, GT("Open"), GT("Open a previously saved project"),),
    (menuid.SAVE, GT("Save"), GT("Save current project"),),
    (menuid.SAVEAS, GT("Save as"), GT("Save current project with a new filename"),),
    None,
    (menuid.QBUILD, GT("Quick Build"), GT("Build a package from an existing build tree"), ICON_CLOCK,),
    None,
    (menuid.EXIT, GT("Quit"), GT("Exit Debreate"),),
    ]

  if testing:
    mitems_file.append((menuid.ALIEN, GT("Convert packages"), GT("Convert between package types")))

  # Adding all menus to menu bar

  mitems = (
    mitems_file,
    )

  for menu_list in mitems:
    for mitem in menu_list:
      if not mitem:
        menu_file.AppendSeparator()

      else:
        itm = wx.MenuItem(menu_file, mitem[0], mitem[1], mitem[2])
        if len(mitem) > 3:
          itm.SetBitmap(mitem[3])

        menu_file.Append(itm)

  # ----- Options Menu
  parent.menu_opt = wx.Menu()

  # Show/Hide tooltips
  parent.opt_tooltips = wx.MenuItem(parent.menu_opt, menuid.TOOLTIPS, GT("Show tooltips"),
      GT("Show or hide tooltips"), kind=wx.ITEM_CHECK)

  # A bug with wx 2.8 does not allow tooltips to be toggled off
  if wx.MAJOR_VERSION > 2:
    parent.menu_opt.Append(parent.opt_tooltips)

  if parent.menu_opt.FindItemById(menuid.TOOLTIPS):
    show_tooltips = config.get("user").getBool("tooltips", dbr.config.getDefault("tooltips"))
    if show_tooltips != ConfCode.KEY_NO_EXIST:
      parent.opt_tooltips.Check(show_tooltips)

    else:
      parent.opt_tooltips.Check(GetDefaultConfigValue("tooltips"))

  # *** Option Menu: open logs directory *** #

  if paths.getExecutable("xdg-open"):
    mitm_logs_open = wx.MenuItem(parent.menu_opt, menuid.OPENLOGS, GT("Open logs directory"))
    parent.menu_opt.Append(mitm_logs_open)

    parent.Bind(wx.EVT_MENU, parent.OnLogDirOpen, id=menuid.OPENLOGS)

  # *** app cache *** #

  menu_cache = wx.Menu()

  mitm_ccache = wx.MenuItem(menu_cache, menuid.CCACHE, GT("Clear local cache"))
  opt_distname_cache = wx.MenuItem(menu_cache, menuid.DIST, GT("Update dist names cache"),
      GT("Creates/Updates list of distribution names for changelog page"))
  if testing:
    cache_lint_tags = wx.MenuItem(menu_cache, menuid.LINTTAGS, GT("Cache lintian tags"),
        GT("Downloads list of available tags recognized by lintian"))

  menu_cache.Append(mitm_ccache)
  menu_cache.AppendSeparator()
  menu_cache.Append(opt_distname_cache)
  if testing:
    menu_cache.Append(cache_lint_tags)
  parent.menu_opt.AppendSubMenu(menu_cache, GT("Cache"))

  # ----- Help Menu
  menu_help = wx.Menu()

  # ----- Version update
  mitm_update = wx.MenuItem(menu_help, menuid.UPDATE, GT("Check for update"),
      GT("Check if a new version is available for download"))
  mitm_update.SetBitmap(ICON_LOGO)

  menu_help.Append(mitm_update)
  menu_help.AppendSeparator()

  # Menu with links to the Debian Policy Manual webpages
  parent.menu_policy = wx.Menu()

  policy_links = (
    (refid.DPM, GT("Debian Policy Manual"),
        "https://www.debian.org/doc/debian-policy",),
    (refid.DPMCtrl, GT("Control files"),
        "https://www.debian.org/doc/debian-policy/ch-controlfields.html",),
    (refid.DPMLog, GT("Changelog"),
        "https://www.debian.org/doc/debian-policy/ch-source.html#s-dpkgchangelog",),
    (refid.LINT_TAGS, GT("Lintian Tags Explanation"),
        "https://lintian.debian.org/tags-all.html",),
    (refid.LINT_OVERRIDE, GT("Overriding Lintian Tags"),
        "https://lintian.debian.org/manual/section-2.4.html",),
    (refid.LAUNCHERS, GT("Launchers / Desktop entries"),
        "https://www.freedesktop.org/wiki/Specifications/desktop-entry-spec/",),
    # Unofficial links
    None,
    (refid.DEBSRC, GT("Building debs from Source"),
        "http://www.quietearth.us/articles/2006/08/16/Building-deb-package-from-source",), # This is here only temporarily for reference
    (refid.MAN, GT("Writing manual pages"),
        "https://liw.fi/manpages/",),
    )

  for LINK in policy_links:
    if not LINK:
      parent.menu_policy.AppendSeparator()

    elif len(LINK) > 2:
      link_id = LINK[0]
      label = LINK[1]
      url = LINK[2]

      if len(LINK) > 3:
        icon = LINK[3]

      else:
        icon = ICON_GLOBE

      mitm = wx.MenuItem(parent.menu_policy, link_id, label, url)
      mitm.SetBitmap(icon)
      parent.menu_policy.Append(mitm)

      parent.Bind(wx.EVT_MENU, parent.OpenPolicyManual, id=link_id)

  mitm_manual = wx.MenuItem(menu_help, wx.ID_HELP, GT("Manual"), GT("Open a usage document"))
  mitm_about = wx.MenuItem(menu_help, wx.ID_ABOUT, GT("About"), GT("About Debreate"))

  menu_help.Append(-1, GT("Reference"), parent.menu_policy)
  menu_help.AppendSeparator()
  menu_help.Append(mitm_manual)
  menu_help.Append(mitm_about)

  if parent.menu_opt.GetMenuItemCount():
    menubar.Append(parent.menu_opt, GT("Options"), menuid.OPTIONS)
  menubar.Append(menu_help, GT("Help"), menuid.HELP)

  # catching menu events

  parent.Bind(wx.EVT_MENU, parent.OnClearCache, id=menuid.CCACHE)
  return menubar
