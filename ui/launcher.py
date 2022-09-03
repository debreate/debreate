## \package ui.launcher

# MIT licensing
# See: docs/LICENSE.txt


import os, shutil, wx

from wx.adv import OwnerDrawnComboBox

from dbr.language       import GT
from dbr.log            import DebugEnabled
from dbr.log            import Logger
from f_export.ofield    import OutputField
from f_export.permiss   import SetFileExecutable
from globals.errorcodes import dbrerrno
from globals.fileio     import ReadFile
from globals.fileio     import WriteFile
from globals.ident      import btnid
from globals.ident      import chkid
from globals.ident      import inputid
from globals.ident      import listid
from globals.ident      import page_ids
from globals.strings    import GS
from globals.strings    import TextIsEmpty
from input.list         import ListCtrl
from input.list         import ListCtrlBase
from input.select       import ComboBoxESS
from input.text         import TextAreaESS
from input.toggle       import CheckBoxCFG
from input.toggle       import CheckBoxESS
from ui.button          import CreateButton
from ui.checklist       import CheckList
from ui.dialog          import ConfirmationDialog
from ui.dialog          import GetFileOpenDialog
from ui.dialog          import GetFileSaveDialog
from ui.dialog          import ShowDialog
from ui.dialog          import ShowErrorDialog
from ui.layout          import BoxSizer
from ui.panel           import BorderedPanel
from ui.panel           import ScrolledPanel
from ui.panel           import SectionedPanel
from ui.textpreview     import TextPreview
from wiz.helper         import ErrorTuple
from wiz.helper         import FieldEnabled
from wiz.helper         import GetField
from wiz.helper         import GetMainWindow
from wiz.wizard         import WizardPage


## Template for individual launchers
class LauncherTemplate(ScrolledPanel):
  def __init__(self, parent, win_id=wx.ID_ANY, name="launcher"):
    ScrolledPanel.__init__(self, parent, win_id, name=name)

    # --- Buttons to open/preview/save .desktop file
    btn_open = CreateButton(self, btnid.BROWSE, GT("Browse"), "browse", name="btn browse")
    btn_save = CreateButton(self, btnid.SAVE, GT("Save"), "save", name="btn save")
    btn_preview = CreateButton(self, btnid.PREVIEW, GT("Preview"), "preview", name="btn preview")

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
    ti_mime = TextAreaESS(self, inputid.MIME, defaultValue=wx.EmptyString, name="MimeType",
        outLabel="MimeType")

    # ----- OTHER/CUSTOM
    txt_other = wx.StaticText(self, label=GT("Custom Fields"), name="other")
    btn_other = CreateButton(self, label=GT("Other"), image="add", name="btn other")
    btn_rm_other = CreateButton(self, btnid.REMOVE, GT("Remove Other"), "remove",
        name="btn rm other")
    pnl_other = SectionedPanel(self, inputid.OTHER)

    btn_rm_other.Enable(pnl_other.HasSelected())

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
    btn_catclr = CreateButton(self, btnid.CLEAR, GT("Clear"), "clear", name="clear category")
    lst_categories = CheckList(self, listid.CAT, opts_category, name="Categories")

    if not lst_categories.HasSelected():
      btn_catclr.Disable()

    txt_catcustom = wx.StaticText(self, label=GT("Custom Categories (Separate by \",\" or \";\")"))
    # Set to 'True' to list custom categories first
    # FIXME: Should this be saved to project instead of config???
    chk_catcustom = CheckBoxCFG(self, chkid.CAT, GT("List first"), name="chk catcustom",
        cfgKey="prioritize custom categories")
    ti_catcustom = TextAreaESS(self, inputid.CAT2, name="category custom")

    # *** Event Handling *** #

    btn_open.Bind(wx.EVT_BUTTON, self.OnLoadLauncher)
    btn_save.Bind(wx.EVT_BUTTON, self.OnExportLauncher)
    btn_preview.Bind(wx.EVT_BUTTON, self.OnPreviewLauncher)

    btn_other.Bind(wx.EVT_BUTTON, self.OnOtherAdd)
    btn_rm_other.Bind(wx.EVT_BUTTON, self.OnOtherRemove)

    btn_catclr.Bind(wx.EVT_BUTTON, self.OnClearCategories)

    wx.EVT_CHECKBOX(self, inputid.OTHER, self.OnOtherSelect)
    wx.EVT_CHECKBOX(self, listid.CAT, self.OnCatSelect)

    # *** Layout *** #

    LEFT_CENTER = wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL
    LEFT_BOTTOM = wx.ALIGN_LEFT|wx.ALIGN_BOTTOM
    RIGHT_BOTTOM = wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM

    lyt_opts1 = wx.FlexGridSizer()
    lyt_opts1.SetCols(3)
    lyt_opts1.SetRows(2)

    lyt_opts1.Add(txt_type, 0, LEFT_CENTER)
    lyt_opts1.Add(ti_type, 0, wx.EXPAND|wx.LEFT, 5)
    lyt_opts1.Add(chk_term, 0, LEFT_CENTER|wx.LEFT, 5)
    lyt_opts1.Add(txt_enc, 0, LEFT_CENTER|wx.TOP, 5)
    lyt_opts1.Add(ti_enc, 0, wx.LEFT|wx.TOP, 5)
    lyt_opts1.Add(chk_notify, 0, LEFT_CENTER|wx.LEFT|wx.TOP, 5)

    lyt_top = BoxSizer(wx.HORIZONTAL)
    lyt_top.Add(lyt_opts1, 0, wx.EXPAND|wx.ALIGN_BOTTOM)
    lyt_top.AddStretchSpacer(1)
    lyt_top.Add(btn_open, 0, wx.ALIGN_TOP)
    lyt_top.Add(btn_save, 0, wx.ALIGN_TOP)
    lyt_top.Add(btn_preview, 0, wx.ALIGN_TOP)

    lyt_mid = wx.GridBagSizer()
    lyt_mid.SetCols(4)
    lyt_mid.AddGrowableCol(1)
    lyt_mid.AddGrowableCol(3)

    # Row 1
    row = 0
    lyt_mid.Add(txt_name, (row, 0), flag=LEFT_CENTER)
    lyt_mid.Add(ti_name, (row, 1), flag=wx.EXPAND|wx.LEFT, border=5)
    lyt_mid.Add(txt_exec, (row, 2), flag=LEFT_CENTER|wx.LEFT, border=5)
    lyt_mid.Add(ti_exec, (row, 3), flag=wx.EXPAND|wx.LEFT, border=5)

    # Row 2
    row += 1
    lyt_mid.Add(txt_comm, (row, 0), flag=LEFT_CENTER|wx.TOP, border=5)
    lyt_mid.Add(ti_comm, (row, 1), flag=wx.EXPAND|wx.LEFT|wx.TOP, border=5)
    lyt_mid.Add(txt_icon, (row, 2), flag=LEFT_CENTER|wx.LEFT|wx.TOP, border=5)
    lyt_mid.Add(ti_icon, (row, 3), flag=wx.EXPAND|wx.LEFT|wx.TOP, border=5)

    # Row 3
    row += 1
    lyt_mid.Add(txt_mime, (row, 0), flag=LEFT_CENTER|wx.TOP, border=5)
    lyt_mid.Add(ti_mime, (row, 1), flag=wx.EXPAND|wx.LEFT|wx.TOP, border=5)

    lyt_bottom = wx.GridBagSizer()

    row = 0
    lyt_bottom.Add(txt_other, (row, 0), flag=LEFT_BOTTOM)
    lyt_bottom.Add(btn_other, (row, 1), flag=RIGHT_BOTTOM)
    lyt_bottom.Add(btn_rm_other, (row, 2), flag=RIGHT_BOTTOM)
    lyt_bottom.Add(txt_category, (row, 3), flag=LEFT_BOTTOM|wx.LEFT, border=5)
    lyt_bottom.Add(btn_catclr, (row, 4), flag=RIGHT_BOTTOM)

    row += 1
    lyt_bottom.Add(pnl_other, (row, 0), (3, 3), wx.EXPAND)
    lyt_bottom.Add(lst_categories, (row, 3), (1, 2), wx.EXPAND|wx.LEFT, 5)

    row += 1
    lyt_bottom.Add(txt_catcustom, (row, 3), flag=LEFT_BOTTOM|wx.LEFT|wx.TOP, border=5)
    lyt_bottom.Add(chk_catcustom, (row, 4), flag=RIGHT_BOTTOM)

    row += 1
    lyt_bottom.Add(ti_catcustom, (row, 3), (1, 2), flag=wx.EXPAND|wx.LEFT, border=5)

    lyt_bottom.AddGrowableRow(1)
    lyt_bottom.AddGrowableCol(1)
    lyt_bottom.AddGrowableCol(3)

    # --- Page 5 Sizer --- #
    lyt_main = BoxSizer(wx.VERTICAL)
    lyt_main.AddSpacer(5)
    lyt_main.Add(lyt_top, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
    lyt_main.Add(lyt_mid, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5)
    lyt_main.Add(lyt_bottom, 1, wx.EXPAND|wx.ALL, 5)

    self.SetAutoLayout(True)
    self.SetSizer(lyt_main)
    self.Layout()


  ## TODO: Doxygen
  def Export(self, out_dir, out_name=wx.EmptyString, executable=False):
    if out_name == wx.EmptyString:
      out_name = page_ids[self.GetId()].upper()

    ret_code = WizardPage.Export(self, out_dir, out_name)

    absolute_filename = "{}/{}".format(out_dir, out_name).replace("//", "/")
    if executable:
      os.chmod(absolute_filename, 0o0755)

    Logger.Debug(__name__, GT("Output filename: {}").format(out_name))

    return ret_code


  ## TODO: Doxygen
  def ExportBuild(self, stage):
    stage = "{}/usr/share/applications".format(stage).replace("//", "/")

    if not os.path.isdir(stage):
      os.makedirs(stage)

    ret_code = self.Export(stage, "{}.desktop".format(self.GetOutputFilename()))
    if ret_code:
      return (ret_code, GT("Could not export menu launcher"))

    return (0, None)


  ## Saves launcher information to text file
  #
  #  \param target
  #    Filename path to export
  #  \param executable
  #    Set executable flag on target filename if True
  def ExportToFile(self, target, executable=False):
    launcher = self.GetLauncherInfo()

    WriteFile(target, launcher)

    return SetFileExecutable(target)


  ## Retrieves Desktop Entry file output information
  #
  #  \return
  #    Text formatted for desktop entry file output
  def Get(self, getModule=False):
    l_lines = ["[Desktop Entry]"]
    categories = []

    id_list = (
      inputid.VERSION,
      inputid.ENC,
      inputid.NAME,
      inputid.EXEC,
      inputid.DESCR,
      inputid.ICON,
      inputid.TYPE,
      chkid.TERM,
      chkid.NOTIFY,
      inputid.MIME,
      listid.CAT,
      inputid.CAT2,
      inputid.OTHER,
      )

    for ID in id_list:
      key = wx.EmptyString
      value = wx.EmptyString
      field = None

      # TODO: Allow setting custom launcher version
      if ID == inputid.VERSION:
        key = "Version"
        value = "1.0"

      else:
        field = GetField(self, ID)

      if field:
        if isinstance(field, ErrorTuple):
          Logger.Warn(__name__, field.GetMessage())

          continue

        if ID == inputid.OTHER:
          for INDEX in range(field.GetSectionCount()):
            section = field.GetSection(INDEX)

            if isinstance(section, CustomSection):
              key = section.GetKey().strip()
              value = section.GetValue().strip()

            if not TextIsEmpty(key) and not TextIsEmpty(value):
              l_lines.append("{}={}".format(key, value))

          continue

        elif ID in (listid.CAT, inputid.CAT2):
          if ID == inputid.CAT2:
            custom_cats = []

            for C1 in field.GetValue().split(","):
              for C2 in C1.split(";"):
                if not TextIsEmpty(C2):
                  custom_cats.append(C2.strip())

            if GetField(self, chkid.CAT).GetValue():
              for LABEL in reversed(custom_cats):
                categories.insert(0, LABEL)

            else:
              for LABEL in custom_cats:
                categories.append(LABEL)

          else:
            for LABEL in field.GetCheckedLabels():
              categories.append(LABEL)

        else:
          if isinstance(field, OutputField):
            key = field.GetOutLabel()

          else:
            key = field.GetName()

          value = wx.EmptyString

          if isinstance(field, (wx.TextCtrl, OwnerDrawnComboBox,)):
            value = field.GetValue().strip()

          elif isinstance(field, wx.CheckBox):
            value = GS(field.GetValue()).lower()

          elif isinstance(field, (ListCtrlBase, ListCtrl,)):
            value = ";".join(field.GetListTuple())

            if not value.endswith(";"):
              value = "{};".format(value)

      if not TextIsEmpty(key) and not TextIsEmpty(value):
        l_lines.append("{}={}".format(key, value))

    # FIXME: Categories should be organized manually by user
    if categories:
      categories = ";".join(categories)
      if not categories.endswith(";"):
        categories = "{};".format(categories)

      l_lines.append("Categories={}".format(categories))

    l_text = "\n".join(l_lines)

    if getModule:
      # FIXME: 'MENU' needed?
      l_text = (__name__, l_text, "MENU")

    return l_text


  ## Formats the launcher information for export
  #
  #  FIXME: Obsolete???
  def GetLauncherInfo(self):
    desktop_list = ["[Desktop Entry]"]

    name = GetField(self, inputid.NAME).GetValue()
    if not TextIsEmpty(name):
      desktop_list.append("Name={}".format(name))

    desktop_list.append("Version=1.0")

    executable = GetField(self, inputid.EXEC).GetValue()
    if not TextIsEmpty(executable):
      desktop_list.append("Exec={}".format(executable))

    comment = GetField(self, inputid.DESCR).GetValue()
    if not TextIsEmpty(comment):
      desktop_list.append("Comment={}".format(comment))

    icon = GetField(self, inputid.ICON).GetValue()
    if not TextIsEmpty(icon):
      desktop_list.append("Icon={}".format(icon))

    launcher_type = GetField(self, inputid.TYPE).GetValue()
    if not TextIsEmpty(launcher_type):
      desktop_list.append("Type={}".format(launcher_type))

    desktop_list.append("Terminal={}".format(GS(self.sel_term.GetSelection() == 0).lower()))

    desktop_list.append("StartupNotify={}".format(GS(self.sel_notify.GetSelection() == 0).lower()))

    encoding = GetField(self, inputid.ENC).GetValue()
    if not TextIsEmpty(encoding):
      desktop_list.append("Encoding={}".format(encoding))

    lst_categories = GetField(self, listid.CAT)
    categories = []
    cat_total = lst_categories.GetItemCount()
    count = 0
    while count < cat_total:
      C = lst_categories.GetItemText(count)
      if not TextIsEmpty(C):
        categories.append(lst_categories.GetItemText(count))

      count += 1

    # Add a final semi-colon if categories is not empty
    if categories:
      categories = ";".join(categories)
      if categories[-1] != ";":
        categories = "{};".format(categories)

      desktop_list.append("Categories={}".format(categories))

    '''
    other = self.ti_other.GetValue()
    if not TextIsEmpty(other):
      desktop_list.append(other)
    '''

    return "\n".join(desktop_list)


  ## Retrieves the filename to be used for the menu launcher
  def GetOutputFilename(self):
    # FIXME: Use tab 'name' or 'title' attribute
    return GetField(self, inputid.NAME).GetValue().strip(" ").replace(" ", "_")


  ## Overrides wiz.wizard.GetRequiredField
  def GetRequiredFields(self, children=None):
    required_fields = list(WizardPage.GetRequiredFields(self, children=children))

    return tuple(required_fields)


  ## TODO: Doxygen
  def ImportFromFile(self, filename):
    Logger.Debug(__name__, GT("Importing page info from {}").format(filename))

    if not os.path.isfile(filename):
      return dbrerrno.ENOENT

    menu_data = ReadFile(filename, split=True, convert=list)

    if "[Desktop Entry]" in menu_data[0]:
      menu_data.remove(menu_data[0])

    menu_definitions = {}
    unused_raw_lines = []

    for L in menu_data:
      if "=" in L:
        key = L.split("=")
        value = key[-1]
        key = key[0]

        menu_definitions[key] = value

        continue

      # Any unrecognizable lines will be added to "Other" section
      unused_raw_lines.append(L)


    def set_value(option):
      key = option.GetName()
      value = None

      if key in menu_definitions:
        value = menu_definitions[key]

        if not TextIsEmpty(value):
          if option in self.opts_input:
            option.SetValue(value)
            return True

          elif option in self.opts_choice:
            if option.SetStringSelection(value):
              return True

          elif option in self.opts_list:
            lst_categories = GetField(self, listid.CAT)

            if key == lst_categories.GetName():
              value = value.split(";")

              if value:
                for X, val in enumerate(value):
                  lst_categories.InsertStringItem(X, val)
                return True

      return False

    categories_used = []

    for group in self.opts_input, self.opts_choice, self.opts_list:
      for O in group:
        if set_value(O):
          categories_used.append(O.GetName())


    # List of keys that can be ignored if unused
    bypass_unused = (
      "Version",
    )

    categories_unused = []
    for key in menu_definitions:
      if key not in categories_used and key not in bypass_unused:
        categories_unused.append("{}={}".format(key, menu_definitions[key]))

    categories_unused += unused_raw_lines
    if len(categories_unused):
      categories_unused = "\n".join(categories_unused)

      #self.ti_other.SetValue(categories_unused)

    return 0


  ## Handles check box events from categories list
  def OnCatSelect(self, event=None):
    btn_cat_clr = GetField(self, wx.ID_CLEAR)
    lst_cat = GetField(self, listid.CAT)

    if btn_cat_clr and lst_cat:
      if FieldEnabled(btn_cat_clr):
        if not lst_cat.HasSelected():
          btn_cat_clr.Disable()

      else:
        if lst_cat.HasSelected():
          btn_cat_clr.Enable()


  ## Handles button event from clear categories button
  def OnClearCategories(self, event=None):
    cats = GetField(self, listid.CAT)

    if cats.HasSelected():
      clear = ConfirmationDialog(GetMainWindow(), GT("Confirm"), GT("Clear categories?"))

      if clear.Confirmed():
        cats.Clear()


  ## Saves launcher information to file
  #
  #  FIXME: Might be problems with reading/writing launchers (see OnLoadLauncher)
  #         'Others' field not being completely filled out.
  def OnExportLauncher(self, event=None):
    Logger.Debug(__name__, "Export launcher ...")

    export = GetFileSaveDialog(GetMainWindow(), GT("Save Launcher"))

    if ShowDialog(export):
      target = export.GetPath()

      # Create a backup file
      # FIXME: Create backup files in WriteFile function?
      overwrite = False
      if os.path.isfile(target):
        backup = "{}.backup".format(target)
        shutil.copy(target, backup)
        overwrite = True

      try:
        self.ExportToFile(target)

        if overwrite:
          os.remove(backup)

      except UnicodeEncodeError:
        detail1 = GT("Unfortunately Debreate does not support unicode yet.")
        detail2 = GT("Remove any non-ASCII characters from your project.")

        ShowErrorDialog(GT("Save failed"), "{}\n{}".format(detail1, detail2), title=GT("Unicode Error"))

        os.remove(target)
        # Restore from backup
        shutil.move(backup, target)


  ## Loads a .desktop launcher's data
  #
  #  FIXME: Might be problems with reading/writing launchers (see OnExportLauncher)
  #         'Others' field not being completely filled out.
  def OnLoadLauncher(self, event=None):
    dia = GetFileOpenDialog(GetMainWindow(), GT("Open Launcher"))

    if ShowDialog(dia):
      path = dia.GetPath()

      data = ReadFile(path, split=True, convert=list)

      # Remove unneeded lines
      if data[0] == "[Desktop Entry]":
        data = data[1:]

      self.Reset()
      # First line needs to be changed to '1'
      data.insert(0, "1")
      self.Set("\n".join(data))


  ## Adds a custom section
  def OnOtherAdd(self, event=None):
    pnl_other = GetField(self, inputid.OTHER)
    pnl_other.AddSection(CustomSection(pnl_other))


  ## Removes selected custom sections
  def OnOtherRemove(self, event=None):
    pnl_other = GetField(self, inputid.OTHER)

    # FIXME: Show confirmation dialog

    if pnl_other:
      if pnl_other.HasSelected():
        remove = ConfirmationDialog(GetMainWindow(), GT("Custom Fields"),
            GT("Remove all selected custom fields?"))

        if remove.Confirmed():
          pnl_other.RemoveSelected()

      btn_remove = GetField(self, wx.ID_REMOVE)

      if btn_remove and FieldEnabled(btn_remove):
        btn_remove.Enable(pnl_other.HasSelected())


  ## Show a preview of the .desktop launcher
  def OnPreviewLauncher(self, event=None):
    preview = TextPreview(title=GT("Menu Launcher Preview"),
        text=self.Get(), size=(500,400))

    ShowDialog(preview)


  ## Handles enabling/disabling the other fields 'remove' button
  def OnOtherSelect(self, event=None):
    btn_remove = GetField(self, wx.ID_REMOVE)
    pnl_other = GetField(self, inputid.OTHER)

    if btn_remove and pnl_other:
      btn_remove.Enable(pnl_other.HasSelected())


  ## TODO: Doxygen
  def Reset(self):
    for O in self.opts_input:
      O.SetValue(O.Default)

    for O in self.opts_choice:
      O.SetSelection(O.Default)

    for O in self.opts_list:
      O.DeleteAllItems()


  ## TODO: Doxygen
  #
  #  FIXME: Deprecated???
  def SetCategory(self, event=None):
    try:
      ID = event.GetKeyCode()

    except AttributeError:
      ID = event.GetEventObject().GetId()

    cat = self.ti_category.GetValue()
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
        if ConfirmationDialog(GetMainWindow(), GT("Confirm"),
            GT("Clear categories?")).ShowModal() in (wx.ID_OK, wx.OK):
          lst_categories.DeleteAllItems()

    if event:
      event.Skip()


  ## Fills out launcher information from loaded file
  #
  #  \param data
  #    Information to fill out menu launcher fields
  #  \param enabled
  #    \b \e bool : Launcher will be flagged for export if True
  def Set(self, data):
    # Make sure we are dealing with a list
    if isinstance(data, str):
      data = data.split("\n")

    # Data list is not empty
    if data:
      Logger.Debug(__name__, "Loading launcher")

      if DebugEnabled():
        for L in data:
          print("  Launcher line: {}".format(L))

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
        )

      for label, control in set_value_fields:
        try:
          control.SetValue(data_defs[label])
          data_defs_remove.append(label)

        except KeyError:
          pass

      # Fields using SetSelection() function
      set_selection_fields = (
        ("Terminal", self.sel_term),
        ("StartupNotify", self.sel_notify),
        )

      for label, control in set_selection_fields:
        try:
          control.SetStringSelection(data_defs[label].lower())
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

          # Remove so not added to misc. list
          misc_defs.pop(index)

          continue
      '''
      if misc_defs:
        self.ti_other.SetValue("\n".join(sorted(misc_defs)))
      '''


## A panel that can be added as a section to ui.panel.SectionedPanel
class CustomSection(BorderedPanel):
  def __init__(self, parent, win_id=wx.ID_ANY):
    BorderedPanel.__init__(self, parent, win_id)

    txt_key = wx.StaticText(self, label=GT("Key"))
    txt_value = wx.StaticText(self, label=GT("Value"))

    ti_key = TextAreaESS(self, inputid.KEY)
    ti_value = TextAreaESS(self, inputid.VALUE)

    # *** Layout *** #

    lyt_input = wx.FlexGridSizer()
    lyt_input.SetRows(2)
    lyt_input.SetCols(2)
    lyt_input.AddGrowableCol(1)

    lyt_input.Add(txt_key, 0, wx.LEFT|wx.TOP, 5)
    lyt_input.Add(txt_value, 0, wx.LEFT|wx.TOP, 5)
    lyt_input.Add(ti_key, 0, wx.LEFT|wx.BOTTOM, 5)
    lyt_input.Add(ti_value, 1, wx.EXPAND|wx.LEFT|wx.BOTTOM, 5)


  ## Retrieves the label to use for key
  def GetKey(self):
    return GetField(self, inputid.KEY).GetValue()


  ## Retrieves the label to use for value
  def GetValue(self):
    return GetField(self, inputid.VALUE).GetValue()
