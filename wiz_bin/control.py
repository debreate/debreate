# -*- coding: utf-8 -*-

## \package wiz_bin.control

# MIT licensing
# See: docs/LICENSE.txt


import os, wx
from wx.combo               import OwnerDrawnComboBox

from dbr.language           import GT
from dbr.log                import Logger
from globals.errorcodes     import dbrerrno
from globals.fileio         import ReadFile
from globals.fileio         import WriteFile
from globals.ident          import inputid
from globals.ident          import pgid
from globals.paths          import ConcatPaths
from globals.strings        import TextIsEmpty
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import FieldEnabled
from globals.wizardhelper   import GetField
from globals.wizardhelper   import GetMainWindow
from globals.wizardhelper   import GetPage
from input.select           import ChoiceESS
from input.select           import ComboBoxESS
from input.text             import TextAreaESS
from input.text             import TextAreaPanelESS
from input.toggle           import CheckBoxESS
from ui.button              import ButtonBrowse64
from ui.button              import ButtonPreview64
from ui.button              import ButtonSave64
from ui.dialog              import GetFileOpenDialog
from ui.dialog              import GetFileSaveDialog
from ui.dialog              import ShowDialog
from ui.dialog              import ShowErrorDialog
from ui.layout              import BoxSizer
from ui.panel               import BorderedPanel
from ui.textpreview         import TextPreview
from ui.wizard              import WizardPage


## This panel displays the field input of the control file
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, pgid.CONTROL)
        
        # Bypass checking this page for build
        # This is mandatory & done manually
        self.prebuild_check = False
        
        self.SetScrollbars(0, 20, 0, 0)
        
        pnl_bg = wx.Panel(self)
        
        # Buttons to open, save, & preview control file
        btn_open = ButtonBrowse64(pnl_bg)
        btn_save = ButtonSave64(pnl_bg)
        btn_preview = ButtonPreview64(pnl_bg)
        
        # *** Required fields *** #
        
        pnl_require = BorderedPanel(pnl_bg)
        
        txt_package = wx.StaticText(pnl_require, label=GT(u'Package'), name=u'package')
        txt_package.req = True
        ti_package = TextAreaESS(pnl_require, inputid.PACKAGE, name=txt_package.Name)
        ti_package.req = True
        
        txt_version = wx.StaticText(pnl_require, label=GT(u'Version'), name=u'version')
        txt_version.req = True
        ti_version = TextAreaESS(pnl_require, inputid.VERSION, name=txt_version.Name)
        ti_version.req = True
        
        txt_maintainer = wx.StaticText(pnl_require, label=GT(u'Maintainer'), name=u'maintainer')
        txt_maintainer.req = True
        ti_maintainer = TextAreaESS(pnl_require, inputid.MAINTAINER, name=txt_maintainer.Name)
        ti_maintainer.req = True
        
        txt_email = wx.StaticText(pnl_require, label=GT(u'Email'), name=u'email')
        txt_email.req = True
        ti_email = TextAreaESS(pnl_require, inputid.EMAIL, name=txt_email.Name)
        ti_email.req = True
        
        opts_arch = (
            u'all', u'alpha', u'amd64', u'arm', u'arm64', u'armeb', u'armel',
            u'armhf', u'avr32', u'hppa', u'i386', u'ia64', u'lpia', u'm32r',
            u'm68k', u'mips', u'mipsel', u'powerpc', u'powerpcspe', u'ppc64',
            u's390', u's390x', u'sh3', u'sh3eb', u'sh4', u'sh4eb', u'sparc',
            u'sparc64',
            )
        
        txt_arch = wx.StaticText(pnl_require, label=GT(u'Architecture'), name=u'architecture')
        sel_arch = ChoiceESS(pnl_require, inputid.ARCH, choices=opts_arch, name=txt_arch.Name)
        sel_arch.default = 0
        sel_arch.SetSelection(sel_arch.default)
        
        # *** Recommended fields *** #
        
        pnl_recommend = BorderedPanel(pnl_bg)
        
        opts_section = (
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
        
        txt_section = wx.StaticText(pnl_recommend, label=GT(u'Section'), name=u'section')
        ti_section = ComboBoxESS(pnl_recommend, choices=opts_section, name=txt_section.Name)
        
        opts_priority = (
            u'optional',
            u'standard',
            u'important',
            u'required',
            u'extra',
            )
        
        txt_priority = wx.StaticText(pnl_recommend, label=GT(u'Priority'), name=u'priority')
        sel_priority = ChoiceESS(pnl_recommend, choices=opts_priority, name=txt_priority.Name)
        sel_priority.default = 0
        sel_priority.SetSelection(sel_priority.default)
        
        txt_synopsis = wx.StaticText(pnl_recommend, label=GT(u'Short Description'), name=u'synopsis')
        ti_synopsis = TextAreaESS(pnl_recommend, name=txt_synopsis.Name)
        
        txt_description = wx.StaticText(pnl_recommend, label=GT(u'Long Description'), name=u'description')
        self.ti_description = TextAreaPanelESS(pnl_recommend, name=txt_description.Name)
        
        # *** Optional fields *** #
        
        pnl_option = BorderedPanel(pnl_bg)
        
        txt_source = wx.StaticText(pnl_option, label=GT(u'Source'), name=u'source')
        ti_source = TextAreaESS(pnl_option, name=txt_source.Name)
        
        txt_homepage = wx.StaticText(pnl_option, label=GT(u'Homepage'), name=u'homepage')
        ti_homepage = TextAreaESS(pnl_option, name=txt_homepage.Name)
        
        txt_essential = wx.StaticText(pnl_option, label=GT(u'Essential'), name=u'essential')
        self.chk_essential = CheckBoxESS(pnl_option, name=u'essential')
        self.chk_essential.default = False
        
        self.grp_input = (
            ti_package,
            ti_version,
            ti_maintainer,  # Maintainer must be listed before email
            ti_email,
            ti_section,
            ti_source,
            ti_homepage,
            ti_synopsis,
            self.ti_description,
            )
        
        self.grp_select = (
            sel_arch,
            sel_priority,
            )
        
        SetPageToolTips(self)
        
        # *** Event Handling *** #
        
        btn_open.Bind(wx.EVT_BUTTON, self.OnBrowse)
        btn_save.Bind(wx.EVT_BUTTON, self.OnSave)
        btn_preview.Bind(wx.EVT_BUTTON, self.OnPreviewControl)
        
        
        # *** Layout *** #
        
        LEFT_BOTTOM = wx.ALIGN_LEFT|wx.ALIGN_BOTTOM
        RIGHT_CENTER = wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT
        
        # Buttons
        lyt_buttons = BoxSizer(wx.HORIZONTAL)
        lyt_buttons.Add(btn_open, 0)
        lyt_buttons.Add(btn_save, 0)
        lyt_buttons.Add(btn_preview, 0)
        
        # Required fields
        lyt_require = wx.FlexGridSizer(0, 4, 5, 5)
        lyt_require.AddGrowableCol(1)
        lyt_require.AddGrowableCol(3)
        
        lyt_require.AddMany((
            (txt_package, 0, RIGHT_CENTER|wx.LEFT|wx.TOP, 5),
            (ti_package, 0, wx.EXPAND|wx.TOP, 5),
            (txt_version, 0, RIGHT_CENTER|wx.TOP, 5),
            (ti_version, 0, wx.EXPAND|wx.TOP|wx.RIGHT, 5),
            (txt_maintainer, 0, RIGHT_CENTER|wx.LEFT, 5),
            (ti_maintainer, 0, wx.EXPAND),
            (txt_email, 0, RIGHT_CENTER, 5),
            (ti_email, 0, wx.EXPAND|wx.RIGHT, 5),
            (txt_arch, 0, RIGHT_CENTER|wx.LEFT|wx.BOTTOM, 5),
            (sel_arch, 0, wx.BOTTOM, 5),
            ))
        
        pnl_require.SetSizer(lyt_require)
        pnl_require.SetAutoLayout(True)
        pnl_require.Layout()
        
        # Recommended fields
        lyt_recommend = wx.GridBagSizer()
        lyt_recommend.SetCols(4)
        lyt_recommend.AddGrowableCol(1)
        lyt_recommend.AddGrowableRow(3)
        
        lyt_recommend.Add(txt_section, (0, 2), flag=RIGHT_CENTER|wx.TOP|wx.BOTTOM, border=5)
        lyt_recommend.Add(ti_section, (0, 3),
                flag=wx.EXPAND|wx.RIGHT|wx.TOP|wx.BOTTOM, border=5)
        lyt_recommend.Add(txt_synopsis, (0, 0), (1, 2), LEFT_BOTTOM|wx.LEFT, 5)
        lyt_recommend.Add(ti_synopsis, (1, 0), (1, 2), wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        lyt_recommend.Add(txt_priority, (1, 2), flag=RIGHT_CENTER, border=5)
        lyt_recommend.Add(sel_priority, (1, 3), flag=wx.EXPAND|wx.RIGHT, border=5)
        lyt_recommend.Add(txt_description, (2, 0), (1, 2), LEFT_BOTTOM|wx.LEFT|wx.TOP, 5)
        lyt_recommend.Add(self.ti_description, (3, 0), (1, 4),
                wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        pnl_recommend.SetSizer(lyt_recommend)
        pnl_recommend.SetAutoLayout(True)
        pnl_recommend.Layout()
        
        # Optional fields
        lyt_option = wx.FlexGridSizer(0, 4, 5, 5)
        
        lyt_option.AddGrowableCol(1)
        lyt_option.AddGrowableCol(3)
        lyt_option.AddSpacer(5)
        lyt_option.AddSpacer(5)
        lyt_option.AddSpacer(5)
        lyt_option.AddSpacer(5)
        lyt_option.AddMany((
            (txt_source, 0, RIGHT_CENTER|wx.LEFT, 5),
            (ti_source, 0, wx.EXPAND),
            (txt_homepage, 0, RIGHT_CENTER, 5),
            (ti_homepage, 0, wx.EXPAND|wx.RIGHT, 5),
            (txt_essential, 0, RIGHT_CENTER|wx.LEFT|wx.BOTTOM, 5),
            (self.chk_essential, 0, wx.BOTTOM, 5),
            ))
        
        pnl_option.SetSizer(lyt_option)
        pnl_option.SetAutoLayout(True)
        pnl_option.Layout()
        
        # Main background panel sizer
        # FIXME: Is background panel (pnl_bg) necessary
        lyt_bg = BoxSizer(wx.VERTICAL)
        lyt_bg.Add(lyt_buttons, 0, wx.ALIGN_RIGHT|wx.BOTTOM, 5)
        lyt_bg.Add(wx.StaticText(pnl_bg, label=GT(u'Required')), 0)
        lyt_bg.Add(pnl_require, 0, wx.EXPAND)
        lyt_bg.Add(wx.StaticText(pnl_bg, label=GT(u'Recommended')), 0, wx.TOP, 5)
        lyt_bg.Add(pnl_recommend, 1, wx.EXPAND)
        lyt_bg.Add(wx.StaticText(pnl_bg, label=GT(u'Optional')), 0, wx.TOP, 5)
        lyt_bg.Add(pnl_option, 0, wx.EXPAND)
        
        pnl_bg.SetAutoLayout(True)
        pnl_bg.SetSizer(lyt_bg)
        pnl_bg.Layout()
        
        # Page's main sizer
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.AddSpacer(5)
        lyt_main.Add(pnl_bg, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## TODO: Doxygen
    def ExportBuild(self, target, installed_size=0):
        self.Export(target, u'control')
        
        absolute_filename = ConcatPaths((target, u'control'))
        
        if not os.path.isfile(absolute_filename):
            return GT(u'Control file was not created')
        
        if installed_size:
            control_data = ReadFile(absolute_filename, split=True, convert=list)
            
            size_line = u'Installed-Size: {}'.format(installed_size)
            if len(control_data) > 3:
                control_data.insert(3, size_line)
            
            else:
                control_data.append(size_line)
            
            # Be sure not to strip trailing newline (dpkg is picky)
            WriteFile(absolute_filename, control_data, no_strip=u'\n')
        
        return GT(u'Control file created: {}').format(absolute_filename)
    
    
    ## Retrieves information for control file export
    #  
    #  \param string_format
    #        \b \e bool : If True, only string-formatted info is returned
    #  \return
    #        \b \e tuple(str, str) : A tuple containing the filename & a string representation of control file formatted for text output
    def Get(self, get_module=False):
        page = self.GetCtrlInfo()
        
        if get_module:
            page = (__name__, page,)
        
        return page
    
    
    ## TODO: Doxygen
    def GetCtrlInfo(self):
        pg_depends = GetPage(pgid.DEPENDS)
        
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
        
        
        if self.chk_essential.GetValue():
            ctrl_list.append(u'Essential: yes')
        
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
        dep_area = GetField(pg_depends, inputid.LIST)
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
        
        # dpkg requires empty newline at end of file
        return u'\n'.join(ctrl_list).strip(u'\n') + u'\n'
    
    
    ## TODO: Doxygen
    def GetPackageName(self):
        return GetField(self, inputid.PACKAGE).GetValue()
    
    
    ## TODO: Doxygen
    #  
    #  TODO: Use 'Set'/'SetPage' method
    def ImportFromFile(self, file_path):
        Logger.Debug(__name__, GT(u'Importing file: {}'.format(file_path)))
        
        if not os.path.isfile(file_path):
            ShowErrorDialog(GT(u'File does not exist: {}'.format(file_path)), linewrap=600)
            return dbrerrno.ENOENT
        
        file_text = ReadFile(file_path)
        
        page_depends = GetPage(pgid.DEPENDS)
        
        # Reset fields to default before opening
        self.Reset()
        page_depends.Reset()
        
        depends_data = self.Set(file_text)
        page_depends.Set(depends_data)
    
    
    ## Tells the build script whether page should be built
    #  
    #  \override ui.wizard.WizardPage.IsExportable
    def IsExportable(self):
        # Build page must always be built
        return True
    
    
    ## TODO: Doxygen
    def OnBrowse(self, event=None):
        browse_dialog = GetFileOpenDialog(GetMainWindow(), GT(u'Open File'))
        if ShowDialog(browse_dialog):
            self.ImportFromFile(browse_dialog.GetPath())
    
    
    ## Show a preview of the control file
    def OnPreviewControl(self, event=None):
        ctrl_info = self.GetCtrlInfo()
        
        preview = TextPreview(title=GT(u'Control File Preview'),
                text=ctrl_info, size=(600,400))
        
        ShowDialog(preview)
    
    
    ## Export control information to text file
    def OnSave(self, event=None):
        # Get data to write to control file
        control = self.GetCtrlInfo()
        
        save_dialog = GetFileSaveDialog(GetMainWindow(), GT(u'Save Control Information'))
        save_dialog.SetFilename(u'control')
        
        if ShowDialog(save_dialog):
            # Be sure not to strip trailing newline (dpkg is picky)
            WriteFile(save_dialog.GetPath(), control, no_strip=u'\n')
    
    
    ## TODO: Doxygen
    #  
    #  FIXME: Unfinished???
    def ReLayout(self):
        # Organize all widgets correctly
        lc_width = self.coauth.GetSize()[0]
        self.coauth.SetColumnWidth(0, lc_width/2)
    
    
    ## Resets all fields on page to default values
    def Reset(self):
        for I in self.grp_input:
            # Calling 'Clear' on ComboBox removes all options
            if isinstance(I, (wx.ComboBox, OwnerDrawnComboBox,)):
                I.SetValue(wx.EmptyString)
            
            else:
                I.Clear()
        
        for S in self.grp_select:
            S.SetSelection(S.default)
        
        self.chk_essential.SetValue(self.chk_essential.default)
    
    
    ## Opening Project/File & Setting Fields
    def Set(self, data):
        # Decode to unicode string if input is byte string
        if isinstance(data, str):
            data = data.decode(u'utf-8')
        
        # Strip leading & trailing spaces, tabs, & newlines
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
                
                if key == self.chk_essential.GetName().title() and value.lower() in (u'yes', u'true'):
                    self.chk_essential.SetValue(True)
                
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
        self.ti_description.SetValue(u'\n'.join(description))
        
        # Return depends data to parent to be sent to page_depends
        return depends_containers
