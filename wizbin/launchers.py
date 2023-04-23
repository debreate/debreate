
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module wizbin.launchers

import os
import shutil

import wx

import ui.app
import ui.page

from dbr.language      import GT
from globals.tooltips  import SetPageToolTips
from input.list        import ListCtrl
from input.select      import ComboBox
from input.select      import ComboBoxESS
from input.text        import TextArea
from input.text        import TextAreaESS
from input.text        import TextAreaPanel
from input.toggle      import CheckBox
from input.toggle      import CheckBoxESS
from libdbr            import strings
from libdbr.fileio     import readFile
from libdbr.fileio     import writeFile
from libdbr.logger     import Logger
from libdebreate.ident import btnid
from libdebreate.ident import chkid
from libdebreate.ident import inputid
from libdebreate.ident import listid
from libdebreate.ident import pgid
from libdebreate.ident import txtid
from ui.button         import CreateButton
from ui.dialog         import ConfirmationDialog
from ui.dialog         import ShowDialog
from ui.dialog         import ShowErrorDialog
from ui.helper         import GetAllTypeFields
from ui.helper         import GetField
from ui.layout         import BoxSizer
from ui.style          import layout as lyt
from ui.textpreview    import TextPreview


logger = Logger(__name__)

## Page for creating a system menu launcher
class Page(ui.page.Page):
  ## Constructor
  #
  #  @param parent
  #      Parent <b><i>wx.Window</i></b> instance
  def __init__(self, parent):
    super().__init__(parent, pgid.MENU) #, name=GT("Menu Launcher"))

    ## Override default label
    self.Label = GT("Menu Launcher")

    # --- Buttons to open/preview/save .desktop file
    btn_open = CreateButton(self, btnid.BROWSE, GT("Browse"), "browse", name="btn browse")
    btn_save = CreateButton(self, btnid.SAVE, GT("Save"), "save", name="btn save")
    btn_preview = CreateButton(self, btnid.PREVIEW, GT("Preview"), "preview", name="btn preview")

    # --- CHECKBOX
    chk_enable = CheckBox(self, chkid.ENABLE, GT("Create system menu launcher"))

    # --- TYPE
    opts_type = ("Application", "Link", "Directory",)

    txt_type = wx.StaticText(self, label=GT("Type"), name="type")
    ti_type = ComboBoxESS(self, inputid.TYPE, choices=opts_type,
        name="Type", defaultValue=opts_type[0])

    # --- ENCODING
    opts_enc = (
      "UTF-1", "UTF-7", "UTF-8", "CESU-8", "UTF-EBCDIC",
      "UTF-16", "UTF-32", "SCSU", "BOCU-1", "Punycode",
      "GB 18030",
      )

    txt_enc = wx.StaticText(self, label=GT("Encoding"), name="encoding")
    ti_enc = ComboBoxESS(self, inputid.ENC, choices=opts_enc, name="Encoding",
        defaultValue=opts_enc[2])

    # --- TERMINAL
    chk_term = CheckBoxESS(self, chkid.TERM, GT("Terminal"), name="Terminal")

    # --- STARTUP NOTIFY
    chk_notify = CheckBoxESS(self, chkid.NOTIFY, GT("Startup Notify"), name="StartupNotify",
        defaultValue=True)

    # --- Custom output filename
    txt_filename = wx.StaticText(self, txtid.FNAME, GT("Filename"), name="filename")
    ti_filename = TextArea(self, inputid.FNAME, name=txt_filename.Name)

    chk_filename = CheckBox(self, chkid.FNAME, GT("Use \"Name\" as output filename (<Name>.desktop)"),
        name="filename chk", defaultValue=True)

    # --- NAME (menu)
    txt_name = wx.StaticText(self, label=GT("Name"), name="name*")
    ti_name = TextAreaESS(self, inputid.NAME, name="Name")
    ti_name.req = True

    # --- EXECUTABLE
    txt_exec = wx.StaticText(self, label=GT("Executable"), name="exec")
    ti_exec = TextAreaESS(self, inputid.EXEC, name="Exec")

    # --- COMMENT
    txt_comm = wx.StaticText(self, label=GT("Comment"), name="comment")
    ti_comm = TextAreaESS(self, inputid.DESCR, name="Comment")

    # --- ICON
    txt_icon = wx.StaticText(self, label=GT("Icon"), name="icon")
    ti_icon = TextAreaESS(self, inputid.ICON, name="Icon")

    txt_mime = wx.StaticText(self, label=GT("MIME Type"), name="mime")
    ti_mime = TextAreaESS(self, inputid.MIME, defaultValue=wx.EmptyString, name="MimeType")

    # ----- OTHER/CUSTOM
    txt_other = wx.StaticText(self, label=GT("Custom Fields"), name="other")
    ti_other = TextAreaPanel(self, inputid.OTHER, name=txt_other.Name)
    ti_other.EnableDropTarget()

    # --- CATEGORIES
    opts_category = (
      "2DGraphics",
      "Accessibility", "Application", "ArcadeGame", "Archiving", "Audio", "AudioVideo",
      "BlocksGame", "BoardGame",
      "Calculator", "Calendar", "CardGame", "Compression", "ContactManagement", "Core",
      "DesktopSettings", "Development", "Dictionary", "DiscBurning", "Documentation",
      "Email",
      "FileManager", "FileTransfer",
      "Game", "GNOME", "Graphics", "GTK",
      "HardwareSettings",
      "InstantMessaging",
      "KDE",
      "LogicGame",
      "Math", "Monitor",
      "Network",
      "OCR", "Office",
      "P2P", "PackageManager", "Photography", "Player", "Presentation", "Printing",
      "Qt",
      "RasterGraphics", "Recorder", "RemoteAccess",
      "Scanning", "Screensaver", "Security", "Settings", "Spreadsheet", "System",
      "Telephony", "TerminalEmulator", "TextEditor",
      "Utility",
      "VectorGraphics", "Video", "Viewer",
      "WordProcessor", "Wine", "Wine-Programs-Accessories",
      "X-GNOME-NetworkSettings", "X-GNOME-PersonalSettings", "X-GNOME-SystemSettings",
      "X-KDE-More", "X-Red-Hat-Base", "X-SuSE-ControlCenter-System",
      )

    txt_category = wx.StaticText(self, label=GT("Categories"), name="category")

    # This option does not get set by importing a new project
    ti_category = ComboBox(self, inputid.CAT, choices=opts_category, name=txt_category.Name,
        defaultValue=opts_category[0])

    btn_catadd = CreateButton(self, btnid.ADD, GT("Add"), "add", name="add category")
    btn_catdel = CreateButton(self, btnid.REMOVE, GT("Remove"), "remove", name="rm category")
    btn_catclr = CreateButton(self, btnid.CLEAR, GT("Clear"), "clear", name="clear category")

    # FIXME: Allow using multi-select + remove
    lst_categories = ListCtrl(self, listid.CAT, name="Categories")
    # Can't set LC_SINGLE_SEL in constructor for wx 3.0 (ListCtrl bug???)
    lst_categories.SetSingleStyle(wx.LC_SINGLE_SEL)

    self.OnToggle()

    SetPageToolTips(self)

    # *** Event Handling *** #

    btn_open.Bind(wx.EVT_BUTTON, self.OnLoadLauncher)
    btn_save.Bind(wx.EVT_BUTTON, self.OnExportLauncher)
    btn_preview.Bind(wx.EVT_BUTTON, self.OnPreviewLauncher)

    chk_enable.Bind(wx.EVT_CHECKBOX, self.OnToggle)

    chk_filename.Bind(wx.EVT_CHECKBOX, self.OnSetCustomFilename)

    ti_category.Bind(wx.EVT_KEY_DOWN, self.SetCategory)
    lst_categories.Bind(wx.EVT_KEY_DOWN, self.SetCategory)
    btn_catadd.Bind(wx.EVT_BUTTON, self.SetCategory)
    btn_catdel.Bind(wx.EVT_BUTTON, self.SetCategory)
    btn_catclr.Bind(wx.EVT_BUTTON, self.OnClearCategories)

    # *** Layout *** #

    LEFT_CENTER = wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL
    LEFT_BOTTOM = lyt.ALGN_LB
    RIGHT_BOTTOM = wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM

    lyt_top = BoxSizer(wx.HORIZONTAL)
    lyt_top.Add(chk_enable, 0, LEFT_BOTTOM)
    lyt_top.AddStretchSpacer(1)
    lyt_top.Add(btn_open, 0, wx.ALIGN_TOP)
    lyt_top.Add(btn_save, 0, wx.ALIGN_TOP|wx.LEFT, 5)
    lyt_top.Add(btn_preview, 0, wx.ALIGN_TOP|wx.LEFT, 5)

    lyt_opts1 = wx.FlexGridSizer(2, 3, 0, 0)

    lyt_opts1.Add(txt_type, 0, LEFT_CENTER)
    lyt_opts1.Add(ti_type, 0, wx.EXPAND|wx.LEFT, 5)
    lyt_opts1.Add(chk_term, 0, LEFT_CENTER|wx.LEFT, 5)
    lyt_opts1.Add(txt_enc, 0, LEFT_CENTER|wx.TOP, 5)
    lyt_opts1.Add(ti_enc, 0, lyt.PAD_LT, 5)
    lyt_opts1.Add(chk_notify, 0, LEFT_CENTER|lyt.PAD_LT, 5)

    lyt_mid = wx.GridBagSizer()
    lyt_mid.SetCols(4)
    lyt_mid.AddGrowableCol(1)
    lyt_mid.AddGrowableCol(3)

    # Row 1
    row = 0
    lyt_mid.Add(txt_filename, (row, 0), flag=LEFT_CENTER)
    lyt_mid.Add(ti_filename, (row, 1), flag=wx.EXPAND|wx.LEFT, border=5)
    lyt_mid.Add(chk_filename, (row, 2), span=(1, 2), flag=LEFT_CENTER|wx.LEFT, border=5)

    # Row 2
    row += 1
    lyt_mid.Add(txt_name, (row, 0), flag=LEFT_CENTER|wx.TOP, border=5)
    lyt_mid.Add(ti_name, (row, 1), flag=wx.EXPAND|lyt.PAD_LT, border=5)
    lyt_mid.Add(txt_exec, (row, 2), flag=LEFT_CENTER|lyt.PAD_LT, border=5)
    lyt_mid.Add(ti_exec, (row, 3), flag=wx.EXPAND|lyt.PAD_LT, border=5)

    # Row 3
    row += 1
    lyt_mid.Add(txt_comm, (row, 0), flag=LEFT_CENTER|wx.TOP, border=5)
    lyt_mid.Add(ti_comm, (row, 1), flag=wx.EXPAND|lyt.PAD_LT, border=5)
    lyt_mid.Add(txt_icon, (row, 2), flag=LEFT_CENTER|lyt.PAD_LT, border=5)
    lyt_mid.Add(ti_icon, (row, 3), flag=wx.EXPAND|lyt.PAD_LT, border=5)

    # Row 4
    row += 1
    lyt_mid.Add(txt_mime, (row, 0), flag=LEFT_CENTER|wx.TOP, border=5)
    lyt_mid.Add(ti_mime, (row, 1), flag=wx.EXPAND|lyt.PAD_LT, border=5)

    lyt_bottom = wx.GridBagSizer()

    row = 0
    lyt_bottom.Add(txt_other, (row, 0), flag=LEFT_BOTTOM)
    lyt_bottom.Add(txt_category, (row, 2), flag=LEFT_BOTTOM|wx.LEFT,
        border=5)
    lyt_bottom.Add(ti_category, (row, 3), flag=LEFT_BOTTOM|wx.LEFT,
        border=5)
    lyt_bottom.Add(btn_catadd, (row, 4), flag=RIGHT_BOTTOM)
    lyt_bottom.Add(btn_catdel, (row, 5), flag=RIGHT_BOTTOM|wx.LEFT,
        border=5)
    lyt_bottom.Add(btn_catclr, (row, 6), flag=RIGHT_BOTTOM|wx.LEFT,
        border=5)

    row += 1
    lyt_bottom.Add(ti_other, (row, 0), (1, 2), wx.EXPAND|wx.TOP, 5)
    lyt_bottom.Add(lst_categories, (row, 2), (1, 5), wx.EXPAND|wx.LEFT|wx.TOP, 5)

    lyt_bottom.AddGrowableRow(1)
    lyt_bottom.AddGrowableCol(1)
    lyt_bottom.AddGrowableCol(4)

    # --- Page 5 Sizer --- #
    lyt_main = BoxSizer(wx.VERTICAL)
    lyt_main.AddSpacer(5)
    lyt_main.Add(lyt_top, 0, wx.EXPAND|lyt.PAD_LR, 5)
    lyt_main.Add(lyt_opts1, 0, wx.EXPAND|lyt.PAD_LRT, 5)
    lyt_main.Add(lyt_mid, 0, wx.EXPAND|lyt.PAD_LRT, 5)
    lyt_main.Add(lyt_bottom, 1, wx.EXPAND|wx.ALL, 5)

    self.SetAutoLayout(True)
    self.SetSizer(lyt_main)
    self.Layout()

  ## @override ui.page.Page.init
  def init(self):
    return True

  ## Retrieves page data for export
  def Get(self):
    return self.GetLauncherInfo()

  ## Formats the launcher information for export
  def GetLauncherInfo(self):
    desktop_list = ["[Desktop Entry]"]

    name = GetField(self, inputid.NAME).GetValue()
    if not strings.isEmpty(name):
      desktop_list.append("Name={}".format(name))

    desktop_list.append("Version=1.0")

    executable = GetField(self, inputid.EXEC).GetValue()
    if not strings.isEmpty(executable):
      desktop_list.append("Exec={}".format(executable))

    comment = GetField(self, inputid.DESCR).GetValue()
    if not strings.isEmpty(comment):
      desktop_list.append("Comment={}".format(comment))

    icon = GetField(self, inputid.ICON).GetValue()
    if not strings.isEmpty(icon):
      desktop_list.append("Icon={}".format(icon))

    launcher_type = GetField(self, inputid.TYPE).GetValue()
    if not strings.isEmpty(launcher_type):
      desktop_list.append("Type={}".format(launcher_type))

    desktop_list.append("Terminal={}".format(strings.toString(GetField(self, chkid.TERM).GetValue()).lower()))

    desktop_list.append("StartupNotify={}".format(strings.toString(GetField(self, chkid.NOTIFY).GetValue()).lower()))

    encoding = GetField(self, inputid.ENC).GetValue()
    if not strings.isEmpty(encoding):
      desktop_list.append("Encoding={}".format(encoding))

    mime_type = GetField(self, inputid.MIME).GetValue()
    if not strings.isEmpty(mime_type):
      desktop_list.append("MimeType={}".format(mime_type))

    lst_categories = GetField(self, listid.CAT)
    categories = []
    cat_total = lst_categories.GetItemCount()
    count = 0
    while count < cat_total:
      C = lst_categories.GetItemText(count)
      if not strings.isEmpty(C):
        categories.append(lst_categories.GetItemText(count))
      count += 1

    # Add a final semi-colon if categories is not empty
    if categories:
      categories = ";".join(categories)
      if categories[-1] != ";":
        categories = "{};".format(categories)
      desktop_list.append("Categories={}".format(categories))

    other = GetField(self, inputid.OTHER).GetValue()
    if not strings.isEmpty(other):
      desktop_list.append(other)

    return "\n".join(desktop_list)

  ## Retrieves the filename to be used for the menu launcher
  def GetOutputFilename(self):
    if not GetField(self, chkid.FNAME).GetValue():
      filename = GetField(self, inputid.FNAME).GetValue().strip(" ").replace(" ", "_")
      if not strings.isEmpty(filename):
        return filename
    return GetField(self, inputid.NAME).GetValue().strip(" ").replace(" ", "_")

  ## @todo Doxygen
  def GetSaveData(self):
    if GetField(self, chkid.ENABLE).GetValue():
      data = self.GetLauncherInfo()
      data = "\n".join(data.split("\n")[1:])
      if not GetField(self, chkid.FNAME).GetValue():
        data = "[FILENAME={}]\n{}".format(GetField(self, inputid.FNAME).GetValue(), data)
      return "<<MENU>>\n1\n{}\n<</MENU>>".format(data)
    else:
      return "<<MENU>>\n0\n<</MENU>>"

  ## @override ui.page.Page.toString
  def toString(self):
    return self.GetSaveData()

  ## @todo Doxygen
  def IsOkay(self):
    return GetField(self, chkid.ENABLE).GetValue()

  ## Handles button event from clear categories button
  def OnClearCategories(self, event=None):
    cats = GetField(self, listid.CAT)
    if cats.GetItemCount():
      clear = ConfirmationDialog(ui.app.getMainWindow(), GT("Confirm"), GT("Clear categories?"))
      if clear.Confirmed():
        cats.DeleteAllItems()

  ## Saves launcher information to file
  #
  #  @todo
  #    FIXME: Might be problems with reading/writing launchers (see OnLoadLauncher) 'Others' field
  #    not being completely filled out.
  def OnExportLauncher(self, event=None):
    logger.debug("Export launcher ...")

    # Get data to write to control file
    menu_data = self.GetLauncherInfo().encode("utf-8")

    dia = wx.FileDialog(ui.app.getMainWindow(), GT("Save Launcher"), os.getcwd(),
      style=wx.FD_SAVE|wx.FD_CHANGE_DIR|wx.FD_OVERWRITE_PROMPT)

    if ShowDialog(dia):
      path = dia.GetPath()

      # Create a backup file
      overwrite = False
      if os.path.isfile(path):
        backup = "{}.backup".format(path)
        shutil.copy(path, backup)
        overwrite = True

      try:
        writeFile(path, menu_data)

        if overwrite:
          os.remove(backup)

      except UnicodeEncodeError:
        detail1 = GT("Unfortunately Debreate does not support unicode yet.")
        detail2 = GT("Remove any non-ASCII characters from your project.")

        ShowErrorDialog(GT("Save failed"), "{}\n{}".format(detail1, detail2), title=GT("Unicode Error"))

        os.remove(path)
        # Restore from backup
        shutil.move(backup, path)

  ## Loads a .desktop launcher's data
  #
  #  @todo
  #    FIXME: Might be problems with reading/writing launchers (see OnExportLauncher) 'Others' field
  #    not being completely filled out.
  def OnLoadLauncher(self, event=None):
    dia = wx.FileDialog(ui.app.getMainWindow(), GT("Open Launcher"), os.getcwd(),
        style=wx.FD_CHANGE_DIR)

    if ShowDialog(dia):
      path = dia.GetPath()

      data = readFile(path).split("\n")

      # Remove unneeded lines
      if data[0] == "[Desktop Entry]":
        data = data[1:]

      self.Reset()
      self.SetLauncherData("\n".join(data))

  ## @todo Doxygen
  def OnPreviewLauncher(self, event=None):
    # Show a preview of the .desktop config file
    config = self.GetLauncherInfo()

    dia = TextPreview(title=GT("Menu Launcher Preview"),
        text=config, size=(500,400))

    dia.ShowModal()
    dia.Destroy()

  ## @todo Doxygen
  def OnSetCustomFilename(self, event=None):
    chk_filename = GetField(self, chkid.FNAME)
    txt_filename = GetField(self, txtid.FNAME)
    ti_filename = GetField(self, inputid.FNAME)

    if not chk_filename.IsEnabled():
      txt_filename.Enable(False)
      ti_filename.Enable(False)
      return

    if chk_filename.GetValue():
      txt_filename.Enable(False)
      ti_filename.Enable(False)
      return

    txt_filename.Enable(True)
    ti_filename.Enable(True)

  ## Enables/Disables fields for creating a launcher
  def OnToggle(self, event=None):
    enabled = GetField(self, chkid.ENABLE).IsChecked()

    # Fields that should not be disabled
    skip_ids = (
      chkid.ENABLE,
      btnid.BROWSE,
      txtid.FNAME,
      )

    for LIST in inputid, chkid, listid, btnid:
      for ID in LIST.IdList:
        if ID not in skip_ids:
          field = GetField(self, ID)

          if isinstance(field, wx.Window):
            field.Enable(enabled)

    # Disable/Enable static text labels
    st_labels = GetAllTypeFields(self, wx.StaticText)
    for ST in st_labels:
      if ST.Id not in skip_ids:
        ST.Enable(enabled)

    self.OnSetCustomFilename()

  ## Resets all fields to default values
  def Reset(self):
    chk_filename = GetField(self, chkid.FNAME)

    chk_filename.SetValue(chk_filename.Default)
    GetField(self, inputid.FNAME).Clear()

    for IDS in inputid, chkid, listid:
      idlist = IDS.IdList

      for ID in idlist:
        field = GetField(self, ID)

        if isinstance(field, wx.Window):
          field.Reset()

    self.OnToggle()

  ## @override ui.page.Page.reset
  def reset(self):
    self.Reset()

  ## @todo Doxygen
  def SetCategory(self, event=None):
    try:
      ID = event.GetKeyCode()

    except AttributeError:
      ID = event.GetEventObject().GetId()

    cat = GetField(self, inputid.CAT).GetValue()
    cat = cat.split()
    cat = "".join(cat)

    lst_categories = GetField(self, listid.CAT)

    if ID in (wx.ID_ADD, wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
      lst_categories.InsertStringItem(lst_categories.GetItemCount(), cat)

    elif ID in (wx.ID_REMOVE, wx.WXK_DELETE):
      if lst_categories.GetItemCount() and lst_categories.GetSelectedItemCount():
        cur_cat = lst_categories.GetFirstSelected()
        lst_categories.DeleteItem(cur_cat)

    elif ID == wx.ID_CLEAR:
      if lst_categories.GetItemCount():
        if ConfirmationDialog(ui.app.getMainWindow(), GT("Confirm"),
            GT("Clear categories?")).ShowModal() in (wx.ID_OK, wx.OK):
          lst_categories.DeleteAllItems()

    if event:
      event.Skip()

  ## Fills out launcher information from loaded file
  #
  #  @param data
  #    Information to fill out menu launcher fields
  #  @param enabled
  #    \b \e bool : Launcher will be flagged for export if True
  def SetLauncherData(self, data, enabled=True):
    # Make sure we are dealing with a list
    if isinstance(data, str):
      data = data.split("\n")

    # Data list is not empty
    if data:
      logger.debug("Loading launcher")

      if data[0].isnumeric():
        enabled = int(data.pop(0)) > 0

      if logger.debugging():
        for L in data:
          print("  Launcher line: {}".format(L))

      logger.debug("Enabling launcher: {}".format(enabled))

      if enabled:
        GetField(self, chkid.ENABLE).SetValue(True)

        data_defs = {}
        data_defs_remove = []
        misc_defs = []

        for L in data:
          if "=" in L:
            if L[0] == "[" and L[-1] == "]":
              key = L[1:-1].split("=")
              value = key[1]
              key = key[0]

              misc_defs.append("{}={}".format(key, value))

            else:
              key = L.split("=")
              value = key[1]
              key = key[0]

              data_defs[key] = value

        # Fields using SetValue() function
        set_value_fields = (
          ("Name", GetField(self, inputid.NAME)),
          ("Exec", GetField(self, inputid.EXEC)),
          ("Comment", GetField(self, inputid.DESCR)),
          ("Icon", GetField(self, inputid.ICON)),
          ("Type", GetField(self, inputid.TYPE)),
          ("Encoding", GetField(self, inputid.ENC)),
          ("MimeType", GetField(self, inputid.MIME))
          )

        for label, control in set_value_fields:
          try:
            control.SetValue(data_defs[label])
            data_defs_remove.append(label)

          except KeyError:
            pass

        check_box_fields = (
          ("Terminal", GetField(self, chkid.TERM)),
          ("StartupNotify", GetField(self, chkid.NOTIFY)),
          )

        for label, control in check_box_fields:
          try:
            if data_defs[label].lower() == "true":
              control.SetValue(True)

            else:
              control.SetValue(False)

            data_defs_remove.append(label)

          except KeyError:
            pass

        try:
          lst_categories = GetField(self, listid.CAT)
          categories = tuple(data_defs["Categories"].split(";"))
          for C in categories:
            lst_categories.InsertStringItem(lst_categories.GetItemCount(), C)

          data_defs_remove.append("Categories")

        except KeyError:
          pass

        for K in data_defs_remove:
          if K in data_defs:
            del data_defs[K]

        # Add any leftover keys to misc/other
        for K in data_defs:
          if K not in ("Version",):
            misc_defs.append("{}={}".format(K, data_defs[K]))

        for index in reversed(range(len(misc_defs))):
          K = misc_defs[index]

          # Set custom filename
          if "FILENAME=" in K:
            filename = K.replace("FILENAME=", "")

            if not strings.isEmpty(filename):
              logger.debug("Setting custom filename: {}".format(filename))

              GetField(self, inputid.FNAME).SetValue(filename)
              GetField(self, chkid.FNAME).SetValue(False)

            # Remove so not added to misc. list
            misc_defs.pop(index)
            continue

        if misc_defs:
          GetField(self, inputid.OTHER).SetValue("\n".join(sorted(misc_defs)))

        self.OnToggle()
