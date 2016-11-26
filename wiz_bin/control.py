# -*- coding: utf-8 -*-

## \package wiz_bin.control


import os, wx
from wx.combo import OwnerDrawnComboBox

from dbr.buttons        import ButtonBrowse64
from dbr.buttons        import ButtonPreview64
from dbr.buttons        import ButtonSave64
from dbr.charctrl       import CharCtrl
from dbr.custom         import OpenFile
from dbr.custom         import SaveFile
from dbr.functions      import FieldEnabled
from dbr.functions      import TextIsEmpty
from dbr.language       import GT
from dbr.log            import Logger
from globals.ident      import FID_EMAIL, ID_DEPENDS
from globals.ident      import FID_MAINTAINER
from globals.ident      import FID_NAME
from globals.ident      import FID_VERSION
from globals.ident      import ID_CONTROL
from globals.tooltips   import SetPageToolTips


## This panel displays the field input of the control file
class Panel(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, ID_CONTROL, name=GT(u'Control'))
        
        self.SetScrollbars(0, 20, 0, 0)
        
        self.bg = wx.Panel(self)
        
        # Buttons to open, save, & preview control file
        btn_open = ButtonBrowse64(self.bg)
        btn_save = ButtonSave64(self.bg)
        btn_preview = ButtonPreview64(self.bg)
        
        txt_package = wx.StaticText(self.bg, label=GT(u'Package'), name=u'package')
        txt_package.req = True
        self.inp_package = CharCtrl(self.bg, FID_NAME, name=txt_package.Name)
        self.inp_package.req = True
        
        txt_version = wx.StaticText(self.bg, label=GT(u'Version'), name=u'version')
        txt_version.req = True
        self.inp_version = CharCtrl(self.bg, FID_VERSION, name=txt_version.Name)
        self.inp_version.req = True
        
        txt_maintainer = wx.StaticText(self.bg, label=GT(u'Maintainer'), name=u'maintainer')
        txt_maintainer.req = True
        self.inp_maintainer = wx.TextCtrl(self.bg, FID_MAINTAINER, name=txt_maintainer.Name)
        self.inp_maintainer.req = True
        
        txt_email = wx.StaticText(self.bg, label=GT(u'Email'), name=u'email')
        txt_email.req = True
        self.inp_email = wx.TextCtrl(self.bg, FID_EMAIL, name=txt_email.Name)
        self.inp_email.req = True
        
        self.opts_arch = (
            u'all', u'alpha', u'amd64', u'arm', u'arm64', u'armeb', u'armel',
            u'armhf', u'avr32', u'hppa', u'i386', u'ia64', u'lpia', u'm32r',
            u'm68k', u'mips', u'mipsel', u'powerpc', u'powerpcspe', u'ppc64',
            u's390', u's390x', u'sh3', u'sh3eb', u'sh4', u'sh4eb', u'sparc',
            u'sparc64',
            )
        
        txt_arch = wx.StaticText(self.bg, label=GT(u'Architecture'), name=u'architecture')
        self.sel_arch = wx.Choice(self.bg, choices=self.opts_arch, name=txt_arch.Name)
        self.sel_arch.default = 0
        self.sel_arch.SetSelection(self.sel_arch.default)
        
        # ***** Recommended Group ***** #
        self.inp_section_opt = (
            u'admin', u'cli-mono', u'comm', u'database', u'devel', u'debug',
            u'doc', u'editors', u'electronics', u'embedded', u'fonts', u'games',
            u'gnome', u'graphics', u'gnu-r', u'gnustep', u'hamradio', u'haskell',
            u'httpd', u'interpreters', u'java', u'kde', u'kernel', u'libs',
            u'libdevel', u'lisp', u'localization', u'mail', u'math',
            u'metapackages', u'misc', u'net', u'news', u'ocaml', u'oldlibs',
            u'otherosfs', u'perl', u'php', u'python', u'ruby', u'science',
            u'shells', u'sound', u'tex', u'text', u'utils', u'vcs', u'video',
            u'web', u'x11', u'xfce', u'zope',
            )
        
        sect_txt = wx.StaticText(self.bg, label=GT(u'Section'), name=u'section')
        self.inp_section = OwnerDrawnComboBox(self.bg, choices=self.inp_section_opt, name=sect_txt.Name)
        
        self.opts_priority = (
            u'optional', u'standard', u'important', u'required', u'extra',
            )
        
        prior_txt = wx.StaticText(self.bg, label=GT(u'Priority'), name=u'priority')
        self.sel_priority = wx.Choice(self.bg, choices=self.opts_priority, name=prior_txt.Name)
        self.sel_priority.default = 0
        self.sel_priority.SetSelection(self.sel_priority.default)
        
        syn_txt = wx.StaticText(self.bg, label=GT(u'Short Description'), name=u'synopsis')
        self.inp_synopsis = wx.TextCtrl(self.bg, name=syn_txt.Name)
        
        desc_txt = wx.StaticText(self.bg, label=GT(u'Long Description'), name=u'description')
        self.inp_description = wx.TextCtrl(self.bg, style=wx.TE_MULTILINE, name=desc_txt.Name)
        
        # ***** Optional Group ***** #
        src_txt = wx.StaticText(self.bg, label=GT(u'Source'), name=u'source')
        self.inp_source = wx.TextCtrl(self.bg, name=src_txt.Name)
        
        url_txt = wx.StaticText(self.bg, label=GT(u'Homepage'), name=u'homepage')
        self.inp_homepage = wx.TextCtrl(self.bg, name=url_txt.Name)
        
        self.opts_essential = (
            u'yes', u'no',
            )
        
        ess_txt = wx.StaticText(self.bg, label=GT(u'Essential'), name=u'essential')
        self.sel_essential = wx.Choice(self.bg, choices=self.opts_essential, name=ess_txt.Name)
        self.sel_essential.default = 1
        self.sel_essential.SetSelection(self.sel_essential.default)
        
        # List all widgets to check if fields have changed after keypress
        # This is for determining if the project is saved
        self.text_widgets = {
            self.inp_package: wx.EmptyString,
            self.inp_version: wx.EmptyString,
            }
        
        self.grp_input = (
            self.inp_package,
            self.inp_version,
            self.inp_maintainer,  # Maintainer must be listed before email
            self.inp_email,
            self.inp_section,
            self.inp_source,
            self.inp_homepage,
            self.inp_synopsis,
            self.inp_description,
            )
        
        self.grp_select = (
            self.sel_arch,
            self.sel_priority,
            self.sel_essential,
            )
        
        SetPageToolTips(self)
        
        # *** Layout *** #
        
        # Buttons
        layout_buttons = wx.BoxSizer(wx.HORIZONTAL)
        layout_buttons.Add(btn_open, 0)
        layout_buttons.Add(btn_save, 0)
        layout_buttons.Add(btn_preview, 0)
        
        # Required fields
        layout_require = wx.FlexGridSizer(0, 4, 5, 5)
        layout_require.AddGrowableCol(1)
        layout_require.AddGrowableCol(3)
        
        layout_require.AddSpacer(5)
        layout_require.AddSpacer(5)
        layout_require.AddSpacer(5)
        layout_require.AddSpacer(5)
        layout_require.AddMany((
            (txt_package), (self.inp_package, 0, wx.EXPAND),
            (txt_version), (self.inp_version, 0, wx.EXPAND),
            (txt_maintainer), (self.inp_maintainer, 0, wx.EXPAND),
            (txt_email), (self.inp_email, 0, wx.EXPAND),
            (txt_arch), (self.sel_arch),
            ))
        
        border_require = wx.StaticBox(self.bg, label=GT(u'Required'))
        bbox_require = wx.StaticBoxSizer(border_require, wx.VERTICAL)
        
        bbox_require.Add(layout_require, 0, wx.EXPAND)
        
        # Recommended fields
        layout_recommend = wx.FlexGridSizer(0, 4, 5, 5)
        layout_recommend.AddGrowableCol(1)
        layout_recommend.AddGrowableCol(3)
        
        layout_recommend.AddSpacer(5)
        layout_recommend.AddSpacer(5)
        layout_recommend.AddSpacer(5)
        layout_recommend.AddSpacer(5)
        layout_recommend.AddMany((
            (sect_txt),
            (self.inp_section, 0, wx.EXPAND),
            (prior_txt),
            (self.sel_priority),
            ))
        
        border_recommend = wx.StaticBox(self.bg, label=GT(u'Recommended'))
        bbox_recommend = wx.StaticBoxSizer(border_recommend, wx.VERTICAL)
        
        bbox_recommend.AddSpacer(5)
        bbox_recommend.Add(layout_recommend, 0, wx.EXPAND)
        bbox_recommend.AddSpacer(5)
        bbox_recommend.AddMany((
            (syn_txt, 0),
            (self.inp_synopsis, 0, wx.EXPAND),
            ))
        bbox_recommend.AddSpacer(5)
        bbox_recommend.AddMany((
            (desc_txt, 0),
            (self.inp_description, 1, wx.EXPAND),
            ))
        
        # Optional fields
        layout_option = wx.FlexGridSizer(0, 4, 5, 5)
        
        layout_option.AddGrowableCol(1)
        layout_option.AddGrowableCol(3)
        layout_option.AddSpacer(5)
        layout_option.AddSpacer(5)
        layout_option.AddSpacer(5)
        layout_option.AddSpacer(5)
        layout_option.AddMany((
            (src_txt), (self.inp_source, 0, wx.EXPAND),
            (url_txt), (self.inp_homepage, 0, wx.EXPAND),
            (ess_txt), (self.sel_essential, 1),
            ))
        
        border_option = wx.StaticBox(self.bg, label=GT(u'Optional'))
        bbox_option = wx.StaticBoxSizer(border_option, wx.VERTICAL)
        
        bbox_option.Add(layout_option, 0, wx.EXPAND)
        
        # Main background panel sizer
        # FIXME: Is background panel (self.bg) necessary
        layout_bg = wx.BoxSizer(wx.VERTICAL)
        layout_bg.Add(layout_buttons, 0, wx.ALL, 5)
        layout_bg.Add(bbox_require, 0, wx.EXPAND|wx.ALL, 5)
        layout_bg.Add(bbox_recommend, 1, wx.EXPAND|wx.ALL, 5)
        layout_bg.Add(bbox_option, 0, wx.EXPAND|wx.ALL, 5)
        
        self.bg.SetAutoLayout(True)
        self.bg.SetSizer(layout_bg)
        self.bg.Layout()
        
        # Page's main sizer
        layout_main = wx.BoxSizer(wx.VERTICAL)
        layout_main.Add(self.bg, 1, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(layout_main)
        self.Layout()
        
        # *** Event Handlers *** #
        
        btn_open.Bind(wx.EVT_BUTTON, self.OnBrowse)
        btn_save.Bind(wx.EVT_BUTTON, self.OnSave)
        btn_preview.Bind(wx.EVT_BUTTON, self.OnPreview)
        
        for widget in self.text_widgets:
            wx.EVT_KEY_DOWN(widget, self.OnKeyDown)
            wx.EVT_KEY_UP(widget, self.OnKeyUp)
    
    
    ## Saving project
    def GatherData(self):
        data = self.GetCtrlInfo()
        return u'<<CTRL>>\n{}<</CTRL>>'.format(data)
    
    
    ## TODO: Doxygen
    def GetCtrlInfo(self):
        main_window = wx.GetApp().GetTopWindow()
        
        ctrl_list = []
        synopsis = None
        description = None
        # Email will be set if maintainer changed to True
        maintainer = False
        
        # Text input fields
        for field in self.grp_input:
            field_name = field.GetName().title()
            field_value = field.GetValue()
            
            if FieldEnabled(field) and not TextIsEmpty(field_value):
                Logger.Debug(__name__, GT(u'Exporting {} field').format(field_name))
                
                # Strip leading & trailing spaces, tabs, & newlines
                field_value = field_value.strip(u' \t\n')
                
                if field_name == u'Synopsis':
                    synopsis = u'{}: {}'.format(u'Description', field_value)
                    continue
                
                if field_name == u'Description':
                    description = field_value.split(u'\n')
                    for line_index in range(len(description)):
                        # Remove trailing whitespace
                        description[line_index] = description[line_index].rstrip()
                        
                        if TextIsEmpty(description[line_index]):
                            # Empty lines are formatted with one space indentation & a period
                            description[line_index] = u' .'
                        
                        else:
                            # All other lines are formatted with one space indentation
                            description[line_index] = u' {}'.format(description[line_index])
                    
                    description = u'\n'.join(description)
                    continue
                
                if field_name in (u'Package', u'Version'):
                    # Don't allow whitespace in package name & version
                    ctrl_list.append(u'{}: {}'.format(field_name, u'-'.join(field_value.split(u' '))))
                    continue
                
                if field_name == u'Email':
                    if maintainer and ctrl_list:
                        # Append email to end of maintainer string
                        for ctrl_index in range(len(ctrl_list)):
                            if ctrl_list[ctrl_index].startswith(u'Maintainer: '):
                                Logger.Debug(__name__, u'Found maintainer')
                                ctrl_list[ctrl_index] = u'{} <{}>'.format(ctrl_list[ctrl_index], field_value)
                                break
                    
                    continue
                
                # Don't use 'continue' on this statement
                if field_name == u'Maintainer':
                    maintainer = True
                
                # The rest of the fields
                ctrl_list.append(u'{}: {}'.format(field_name, field_value))
        
        # Selection box fields
        for field in self.grp_select:
            field_name = field.GetName().title()
            field_value = field.GetStringSelection()
            
            if FieldEnabled(field) and not TextIsEmpty(field_value):
                Logger.Debug(__name__, GT(u'Exporting {} field').format(field_name))
                
                # Strip leading & trailing spaces, tabs, & newlines
                field_value = field_value.strip(u' \t\n')
                
                ctrl_list.append(u'{}: {}'.format(field_name, field_value))
        
        # Dependencies & conflicts
        dep_list = [] # Depends
        pre_list = [] # Pre-Depends
        rec_list = [] # Recommends
        sug_list = [] # Suggests
        enh_list = [] # Enhances
        con_list = [] # Conflicts
        rep_list = [] # Replaces
        brk_list = [] # Breaks
        
        all_deps = {
            u'Depends': dep_list,
            u'Pre-Depends': pre_list,
            u'Recommends': rec_list,
            u'Suggests': sug_list,
            u'Enhances': enh_list,
            u'Conflicts': con_list,
            u'Replaces': rep_list,
            u'Breaks': brk_list,
            }
        
        # Get amount of items to add
        dep_area = main_window.page_depends.dep_area
        dep_count = dep_area.GetItemCount()
        count = 0
        while count < dep_count:
            # Get each item from dependencies page
            dep_type = dep_area.GetItem(count, 0).GetText()
            dep_val = dep_area.GetItem(count, 1).GetText()
            for item in all_deps:
                if dep_type == item:
                    all_deps[item].append(dep_val)
            
            count += 1
        
        for item in all_deps:
            if len(all_deps[item]) != 0:
                ctrl_list.append(u'{}: {}'.format(item, u', '.join(all_deps[item])))
        
        if synopsis:
            ctrl_list.append(synopsis)
            
            # Long description is only added if synopsis is not empty
            if description:
                ctrl_list.append(description)
        
        # FIXME: dpkg requires empty newline at end of control file???
        return u'\n'.join(ctrl_list)
    
    
    ## TODO: Doxygen
    def OnBrowse(self, event=None):
        cont = False
        if wx.GetApp().GetTopWindow().cust_dias.IsChecked():
            dia = OpenFile(self)
            if dia.DisplayModal():
                cont = True
        
        else:
            dia = wx.FileDialog(self, GT(u'Open File'), os.getcwd(), style=wx.FD_CHANGE_DIR)
            if dia.ShowModal() == wx.ID_OK:
                cont = True
        
        if cont:
            file_path = dia.GetPath()
            
            FILE_BUFFER = open(file_path, u'r')
            control_data = FILE_BUFFER.read()
            FILE_BUFFER.close()
            
            page_depends = wx.GetApp().GetTopWindow().GetWizard().GetPage(ID_DEPENDS)
            
            # Reset fields to default before opening
            self.ResetAllFields()
            page_depends.ResetAllFields()
            
            depends_data = self.SetFieldData(control_data)
            page_depends.SetFieldData(depends_data)
    
    
    ## Determins if project has been modified
    def OnKeyDown(self, event=None):
        for widget in self.text_widgets:
            self.text_widgets[widget] = widget.GetValue()
        
        if event:
            event.Skip()
    
    
    ## TODO: Doxygen
    def OnKeyUp(self, event=None):
        main_window = wx.GetApp().GetTopWindow()
        
        modified = False
        for widget in self.text_widgets:
            if widget.GetValue() != self.text_widgets[widget]:
                modified = True
        
        main_window.SetSavedStatus(modified)
        
        if event:
            event.Skip()
    
    
    ## TODO: Doxygen
    def OnPreview(self, event=None):
        # Show a preview of the control file
        control = self.GetCtrlInfo()
        
        dia = wx.Dialog(self, title=GT(u'Control File Preview'), size=(500,400))
        preview = wx.TextCtrl(dia, style=wx.TE_MULTILINE|wx.TE_READONLY)
        preview.SetValue(control)
        
        dia_sizer = wx.BoxSizer(wx.VERTICAL)
        dia_sizer.Add(preview, 1, wx.EXPAND)
        
        dia.SetSizer(dia_sizer)
        dia.Layout()
        
        dia.ShowModal()
        dia.Destroy()
    
    
    ## TODO: Doxygen
    def OnSave(self, event=None):
        main_window = wx.GetApp().GetTopWindow()
        
        # Get data to write to control file
        control = self.GetCtrlInfo().encode(u'utf-8')
        
        cont = False
        
        # Open a "Save Dialog"
        if main_window.cust_dias.IsChecked():
            dia = SaveFile(self, GT(u'Save Control Information'))
            dia.SetFilename(u'control')
            if dia.DisplayModal():
                cont = True
                path = u'{}/{}'.format(dia.GetPath(), dia.GetFilename())
        
        else:
            dia = wx.FileDialog(self, u'Save Control Information', os.getcwd(),
                style=wx.FD_SAVE|wx.FD_CHANGE_DIR|wx.FD_OVERWRITE_PROMPT)
            dia.SetFilename(u'control')
            
            if dia.ShowModal() == wx.ID_OK:
                cont = True
                path = dia.GetPath()
        
        if cont:
            FILE_BUFFER = open(path, u'w')
            FILE_BUFFER.write(control)
            FILE_BUFFER.close()
    
    
    ## TODO: Doxygen
    #  
    #  FIXME: Unfinished???
    def ReLayout(self):
        # Organize all widgets correctly
        lc_width = self.coauth.GetSize()[0]
        self.coauth.SetColumnWidth(0, lc_width/2)
    
    
    ## TODO: Doxygen
    def ResetAllFields(self):
        for I in self.grp_input:
            I.Clear()
        
        for S in self.grp_select:
            S.SetSelection(S.default)
    
    
    ## Opening Project/File & Setting Fields
    def SetFieldData(self, data):
        # Decode to unicode string if input is byte string
        if isinstance(data, str):
            data = data.decode(u'utf-8')
        
        # Strip leading & traling spaces, tabs, & newlines
        data = data.strip(u' \t\n')
        control_data = data.split(u'\n')
        
        # Store Dependencies
        depends_containers = (
            [u'Depends'],
            [u'Pre-Depends'],
            [u'Recommends'],
            [u'Suggests'],
            [u'Enhances'],
            [u'Conflicts'],
            [u'Replaces'],
            [u'Breaks'],
            )
        
        # Anything left over is dumped into this list then into the description field
        description = []
        
        for line in control_data:
            if u': ' in line:
                key = line.split(u': ')
                value = u': '.join(key[1:]) # For dependency fields that have ": " in description
                key = key[0]
                
                Logger.Debug(__name__, u'Found key: {}'.format(key))
                
                # Catch Maintainer
                if key == u'Maintainer':
                    maintainer = value
                    email = None
                    
                    if u'<' in maintainer and maintainer.endswith(u'>'):
                        maintainer = maintainer.split(u'<')
                        email = maintainer[1].strip(u' <>\t')
                        maintainer = maintainer[0].strip(u' \t')
                    
                    for I in self.grp_input:
                        input_name = I.GetName().title()
                        
                        if input_name == u'Maintainer':
                            I.SetValue(maintainer)
                            continue
                        
                        if input_name == u'Email':
                            I.SetValue(email)
                            # NOTE: Maintainer should be listed before email in input list
                            break
                    
                    continue
                
                # Set the rest of the input fields
                for I in self.grp_input:
                    input_name = I.GetName().title()
                    if input_name == u'Synopsis':
                        input_name = u'Description'
                    
                    if key == input_name:
                        I.SetValue(value)
                
                # Set the wx.Choice fields
                for S in self.grp_select:
                    if key == S.GetName().title():
                        S.SetStringSelection(value)
                
                # Set dependencies
                for container in depends_containers:
                    if container and key == container[0]:
                        for dep in value.split(u', '):
                            container.append(dep)
            
            else:
                # Description
                if line.startswith(u' .'):
                    # Add a blank line for lines beginning with a period
                    description.append(wx.EmptyString)
                    continue
                
                if not TextIsEmpty(line) and line.startswith(u' '):
                    # Remove the first space generated in the description
                    description.append(line[1:])
                    continue
                
                if not TextIsEmpty(line):
                    description.append(line)
        
        # Put leftovers in long description
        self.inp_description.SetValue(u'\n'.join(description))
        
        # Return depends data to parent to be sent to page_depends
        return depends_containers
