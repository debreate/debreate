# -*- coding: utf-8 -*-

## \package wiz_bin.changelog

# MIT licensing
# See: docs/LICENSE.txt


import commands, os, wx

from dbr.buttons            import ButtonAdd
from dbr.buttons            import ButtonImport
from dbr.language           import GT
from dbr.log                import Logger
from dbr.pathctrl           import PathCtrl
from dbr.selectinput        import ComboBox
from dbr.textinput          import MonospaceTextArea
from dbr.textinput          import TextAreaPanel
from dbr.wizard             import WizardPage
from globals                import ident
from globals.errorcodes     import dbrerrno
from globals.execute        import GetExecutable
from globals.fileio         import ReadFile
from globals.paths          import ConcatPaths
from globals.strings        import TextIsEmpty
from globals.system         import GetOSDistNames
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import ErrorTuple
from globals.wizardhelper   import GetFieldValue
from globals.wizardhelper   import GetPage
from globals.wizardhelper   import GetTopWindow


## Changelog page
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ident.CHANGELOG)
        
        txt_package = wx.StaticText(self, label=GT(u'Package'), name=u'package')
        self.ti_package = wx.TextCtrl(self, name=txt_package.Name)
        
        txt_version = wx.StaticText(self, label=GT(u'Version'), name=u'version')
        self.ti_version = wx.TextCtrl(self, name=txt_version.Name)
        
        dist_names = GetOSDistNames()
        
        txt_dist = wx.StaticText(self, label=GT(u'Distribution'), name=u'dist')
        
        if dist_names:
            self.ti_dist = ComboBox(self, ident.DIST, choices=dist_names, name=txt_dist.Name)
        
        # Use regular text input if could not retrieve distribution names list
        else:
            self.ti_dist = wx.TextCtrl(self, ident.DIST, name=txt_dist.Name)
        
        self.opts_urgency = (
            u'low',
            u'medium',
            u'high',
            u'emergency',
            )
        
        txt_urgency = wx.StaticText(self, label=GT(u'Urgency'), name=u'urgency')
        self.sel_urgency = wx.Choice(self, choices=self.opts_urgency, name=txt_urgency.Name)
        self.sel_urgency.default = 0
        self.sel_urgency.SetSelection(self.sel_urgency.default)
        
        txt_maintainer = wx.StaticText(self, label=GT(u'Maintainer'), name=u'maintainer')
        self.ti_maintainer = wx.TextCtrl(self, name=txt_maintainer.Name)
        
        txt_email = wx.StaticText(self, label=GT(u'Email'), name=u'email')
        self.ti_email = wx.TextCtrl(self, name=txt_email.Name)
        
        # Changes input
        self.ti_changes = TextAreaPanel(self, size=(20,150), name=u'changes')
        
        # Standard destination of changelog
        self.rb_target_standard = wx.RadioButton(self, label=u'/usr/share/doc/<package>',
                name=u'target default', style=wx.RB_GROUP)
        self.rb_target_standard.default = True
        self.rb_target_standard.SetValue(self.rb_target_standard.default)
        
        # Custom destination of changelog
        # FIXME: Should not use same name as default destination???
        self.rb_target_custom = wx.RadioButton(self, name=self.rb_target_standard.Name)
        
        self.ti_target = PathCtrl(self, value=u'/', default=u'/')
        self.ti_target.SetName(u'target custom')
        
        self.btn_import = ButtonImport(self)
        
        self.btn_add = ButtonAdd(self)
        
        self.dsp_changes = MonospaceTextArea(self, name=u'log')
        self.dsp_changes.EnableDropTarget()
        
        SetPageToolTips(self)
        
        # *** Event Handling *** #
        
        wx.EVT_BUTTON(self.btn_import, -1, self.OnImportFromControl)
        wx.EVT_BUTTON(self.btn_add, -1, self.AddInfo)
        
        # *** Layout *** #
        
        lyt_info = wx.FlexGridSizer(2, 6, 5, 5)
        
        lyt_info.AddGrowableCol(1)
        lyt_info.AddGrowableCol(3)
        lyt_info.AddGrowableCol(5)
        lyt_info.AddMany((
            (txt_package, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (self.ti_package, 1, wx.EXPAND),
            (txt_version, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (self.ti_version, 1, wx.EXPAND),
            (txt_dist, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (self.ti_dist, 1, wx.EXPAND),
            (txt_urgency, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (self.sel_urgency, 1, wx.EXPAND),
            (txt_maintainer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (self.ti_maintainer, 1, wx.EXPAND),
            (txt_email, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (self.ti_email, 1, wx.EXPAND)
            ))
        
        self.border_changes = wx.StaticBox(self, label=GT(u'Changes'), size=(20,20))
        lyt_changes = wx.StaticBoxSizer(self.border_changes, wx.VERTICAL)
        lyt_changes.Add(self.ti_changes, 1, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        
        lyt_target_custom = wx.BoxSizer(wx.HORIZONTAL)
        lyt_target_custom.Add(self.rb_target_custom)
        lyt_target_custom.Add(self.ti_target, 1)
        
        border_dest = wx.StaticBox(self, label=GT(u'Target'))
        lyt_target = wx.StaticBoxSizer(border_dest, wx.VERTICAL)
        lyt_target.AddSpacer(5)
        lyt_target.Add(self.rb_target_standard)
        lyt_target.AddSpacer(5)
        lyt_target.Add(lyt_target_custom, 0, wx.EXPAND)
        lyt_target.AddSpacer(5)
        
        details_sizer = wx.BoxSizer(wx.HORIZONTAL)
        details_sizer.Add(lyt_changes, 1, wx.EXPAND|wx.RIGHT, 5)
        details_sizer.Add(lyt_target)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.btn_import)
        button_sizer.Add(self.btn_add)
        
        lyt_main = wx.StaticBoxSizer(wx.StaticBox(self), wx.VERTICAL)
        lyt_main.AddSpacer(10)
        lyt_main.Add(lyt_info, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        lyt_main.AddSpacer(10)
        lyt_main.Add(details_sizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        lyt_main.Add(button_sizer, 0, wx.LEFT|wx.RIGHT, 5)
        lyt_main.Add(self.dsp_changes, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        lyt_main.AddSpacer(5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## TODO: Doxygen
    def AddInfo(self, event=None):
        changes = self.ti_changes.GetValue()
        if TextIsEmpty(changes):
            wx.MessageDialog(GetTopWindow(), GT(u'List of changes is empty'), GT(u'Warning'),
                    style=wx.OK|wx.ICON_EXCLAMATION).ShowModal()
            return
        
        package = self.ti_package.GetValue()
        version = self.ti_version.GetValue()
        distribution = self.ti_dist.GetValue()
        urgency = self.opts_urgency[self.sel_urgency.GetSelection()]
        info1 = u'{} ({}) {}; urgency={}'.format(package, version, distribution, urgency)
        
        details = []
        for line in changes.split(u'\n'):
            line = line.strip()
            
            # Strip empty lines
            if not TextIsEmpty(line):
                if not details:
                    details.append(u'  * {}'.format(line))
                else:
                    details.append(u'    {}'.format(line))
        
        details.insert(0, wx.EmptyString)
        details.append(wx.EmptyString)
        details = u'\n'.join(details)
        
        maintainer = self.ti_maintainer.GetValue()
        email = self.ti_email.GetValue()
        #date = commands.getoutput("date +\"%a, %d %b %Y %T %z\"")
        # FIXME: Use methods from dbr.functions to get date & time
        date = commands.getoutput(u'date -R')
        info2 = u' -- {} <{}>  {}'.format(maintainer, email, date)
        
        entry = u'\n'.join((info1, details, info2))
        self.dsp_changes.SetValue(u'\n'.join((entry, wx.EmptyString, self.dsp_changes.GetValue())))
    
    
    ## TODO: Doxygen
    def Export(self, out_dir, out_name=wx.EmptyString, compress=False):
        ret_value = WizardPage.Export(self, out_dir, out_name=out_name)
        
        absolute_filename = u'{}/{}'.format(out_dir, out_name).replace(u'//', u'/')
        
        CMD_gzip = GetExecutable(u'gzip')
        
        if compress and CMD_gzip:
            commands.getstatusoutput(u'{} -n9 "{}"'.format(CMD_gzip, absolute_filename))
        
        return ret_value
    
    
    ## TODO: Doxygen
    def ExportBuild(self, stage):
        if self.rb_target_standard.GetValue():
            stage = u'{}/usr/share/doc/{}'.format(stage,
                    GetPage(ident.CONTROL).GetPackageName()).replace(u'//', u'/')
        
        else:
            stage = u'{}/{}'.format(stage, self.ti_target.GetValue()).replace(u'//', u'/')
        
        if not os.path.isdir(stage):
            os.makedirs(stage)
        
        # FIXME: Allow user to set filename
        self.Export(stage, u'changelog', True)
        
        export_summary = GT(u'Changelog export failed')
        changelog = ConcatPaths((stage, u'changelog.gz'))
        
        if os.path.isfile(changelog):
            export_summary = GT(u'Changelog export to: {}').format(changelog)
        
        return(0, export_summary)
    
    
    ## TODO: Doxygen
    def GetChangelog(self):
        return self.dsp_changes.GetValue()
    
    
    ## Retrieves changelog information
    #  
    #  The output is a text file that uses sections defined
    #    by braces ([, ]).
    #  \return
    #        \b \e tuple(str, str) : Filename & formatted string of changelog target & body
    def GetPageInfo(self):
        cl_target = u'DEFAULT'
        
        if self.rb_target_custom.GetValue():
            cl_target = self.ti_target.GetValue()
        
        cl_body = self.dsp_changes.GetValue()
        
        if TextIsEmpty(cl_body):
            return None
        
        return (__name__, u'[TARGET={}]\n\n[BODY]\n{}'.format(cl_target, cl_body))
    
    
    ## TODO: Doxygen
    def OnImportFromControl(self, event=None):
        fields = (
            (self.ti_package, ident.F_NAME),
            (self.ti_version, ident.F_VERSION),
            (self.ti_maintainer, ident.F_MAINTAINER),
            (self.ti_email, ident.F_EMAIL),
            )
        
        for F, FID in fields:
            field_value = GetFieldValue(ident.CONTROL, FID)
            
            if isinstance(field_value, ErrorTuple):
                err_msg1 = GT(u'Got error when attempting to retrieve field value')
                err_msg2 = u'\tError code: {}\n\tError message: {}'.format(field_value.GetCode(), field_value.GetString())
                Logger.Error(__name__, u'{}:\n{}'.format(err_msg1, err_msg2))
                
                continue
            
            if not TextIsEmpty(field_value):
                F.SetValue(field_value)
    
    
    ## TODO: Doxygen
    def ImportPageInfo(self, filename):
        if not os.path.isfile(filename):
            return dbrerrno.ENOENT
        
        clog_data = ReadFile(filename, split=True)
        
        sections = {}
        
        def parse_section(key, lines):
            value = u'\n'.join(lines).split(u'\n[')[0]
            
            if u'=' in key:
                key = key.split(u'=')
                value = (key[-1], value)
                key = key[0]
            
            sections[key] = value
        
        # NOTE: This would need to be changed were more sections added to project file
        for L in clog_data:
            line_index = clog_data.index(L)
            
            if not TextIsEmpty(L) and u'[' in L and u']' in L:
                L = L.split(u'[')[-1].split(u']')[0]
                parse_section(L, clog_data[line_index+1:])
        '''
        if u'BODY' in sections:
            self.dsp_changes.SetValue(sections[u'BODY'])
        '''
        
        for S in sections:
            Logger.Debug(__name__, GT(u'Changelog section: "{}", Value:\n{}').format(S, sections[S]))
            
            if isinstance(sections[S], (tuple, list)):
                value_index = 0
                for I in sections[S]:
                    Logger.Debug(__name__, GT(u'Value {}: {}').format(value_index, I))
                    value_index += 1
            
            if S == u'TARGET':
                Logger.Debug(__name__, u'SECTION TARGET FOUND')
                
                if sections[S][0] == u'DEFAULT':
                    Logger.Debug(__name__, u'Using default target')
                    
                    self.rb_target_standard.SetValue(True)
                
                else:
                    Logger.Debug(__name__, GT(u'Using custom target: {}').format(sections[S][0]))
                    
                    self.rb_target_custom.SetValue(True)
                    self.ti_target.SetValue(sections[S][0])
                
                continue
            
            if S == u'BODY':
                Logger.Debug(__name__, u'SECTION BODY FOUND')
                
                self.dsp_changes.SetValue(sections[S])
                
                continue
        
        return 0
    
    
    ## TODO: Doxygen
    def IsExportable(self):
        return not TextIsEmpty(self.dsp_changes.GetValue())
    
    
    ## TODO: Doxygen
    def ResetPageInfo(self):
        self.ti_target.Reset()
        self.dsp_changes.Clear()
    
    
    ## TODO: Doxygen
    def SetChangelogLegacy(self, data):
        changelog = data.split(u'\n')
        dest = changelog[0].split(u'<<DEST>>')[1].split(u'<</DEST>>')[0]
        if dest == u'DEFAULT':
            self.rb_target_standard.SetValue(True)
        
        else:
            self.rb_target_custom.SetValue(True)
            self.ti_target.SetValue(dest)
        
        self.dsp_changes.SetValue(u'\n'.join(changelog[1:]))
