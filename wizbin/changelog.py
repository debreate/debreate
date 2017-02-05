# -*- coding: utf-8 -*-

## \package wizbin.changelog

# MIT licensing
# See: docs/LICENSE.txt


import commands, os, wx

from dbr.language           import GT
from dbr.log                import Logger
from f_export.ftarget       import FileOTarget
from globals.bitmaps        import ICON_WARNING
from globals.changes        import FormatChangelog
from globals.errorcodes     import dbrerrno
from globals.execute        import GetExecutable
from globals.fileio         import ReadFile
from globals.ident          import btnid
from globals.ident          import chkid
from globals.ident          import inputid
from globals.ident          import pgid
from globals.ident          import selid
from globals.paths          import ConcatPaths
from globals.strings        import TextIsEmpty
from globals.system         import GetOSDistNames
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import ErrorTuple
from globals.wizardhelper   import GetFieldValue
from globals.wizardhelper   import GetMainWindow
from input.pathctrl         import PathCtrlESS
from input.select           import Choice
from input.select           import ComboBox
from input.text             import TextArea
from input.text             import TextAreaPanel
from input.text             import TextAreaPanelESS
from input.toggle           import CheckBox
from input.toggle           import CheckBoxESS
from ui.button              import CreateButton
from ui.dialog              import DetailedMessageDialog
from ui.layout              import BoxSizer
from wiz.wizard             import WizardPage


## Changelog page
class Page(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, pgid.CHANGELOG)
        
        txt_package = wx.StaticText(self, label=GT(u'Package'), name=u'package')
        self.ti_package = TextArea(self, inputid.PACKAGE, name=txt_package.Name)
        
        txt_version = wx.StaticText(self, label=GT(u'Version'), name=u'version')
        self.ti_version = TextArea(self, inputid.VERSION, name=txt_version.Name)
        
        dist_names = GetOSDistNames()
        
        txt_dist = wx.StaticText(self, label=GT(u'Distribution'), name=u'dist')
        
        if dist_names:
            self.ti_dist = ComboBox(self, inputid.DIST, choices=dist_names, name=txt_dist.Name)
        
        # Use regular text input if could not retrieve distribution names list
        else:
            self.ti_dist = TextArea(self, inputid.DIST, name=txt_dist.Name)
        
        opts_urgency = (
            u'low',
            u'medium',
            u'high',
            u'emergency',
            )
        
        txt_urgency = wx.StaticText(self, label=GT(u'Urgency'), name=u'urgency')
        self.sel_urgency = Choice(self, selid.URGENCY, choices=opts_urgency, name=txt_urgency.Name)
        
        txt_maintainer = wx.StaticText(self, label=GT(u'Maintainer'), name=u'maintainer')
        self.ti_maintainer = TextArea(self, inputid.MAINTAINER, name=txt_maintainer.Name)
        
        txt_email = wx.StaticText(self, label=GT(u'Email'), name=u'email')
        self.ti_email = TextArea(self, inputid.EMAIL, name=txt_email.Name)
        
        btn_import = CreateButton(self, GT(u'Import'), u'import', btnid.IMPORT, name=u'btn import')
        txt_import = wx.StaticText(self, label=GT(u'Import information from Control page'))
        
        # Changes input
        self.ti_changes = TextAreaPanel(self, size=(20,150), name=u'changes')
        
        # *** Target installation directory
        
        # FIXME: Should this be set by config or project file???
        self.pnl_target = FileOTarget(self, u'/usr/share/doc/<package>' , name=u'target default',
                defaultType=CheckBoxESS, customType=PathCtrlESS, pathIds=(chkid.TARGET, inputid.TARGET,))
        
        self.btn_add = CreateButton(self, GT(u'Add'), u'add', btnid.ADD, name=u'btn add')
        txt_add = wx.StaticText(self, label=GT(u'Insert new changelog entry'))
        
        self.chk_indentation = CheckBox(self, label=GT(u'Preserve indentation'), name=u'indent')
        
        self.dsp_changes = TextAreaPanelESS(self, inputid.CHANGES, monospace=True, name=u'log')
        self.dsp_changes.EnableDropTarget()
        
        SetPageToolTips(self)
        
        # *** Event Handling *** #
        
        btn_import.Bind(wx.EVT_BUTTON, self.OnImportFromControl)
        self.btn_add.Bind(wx.EVT_BUTTON, self.AddInfo)
        
        # *** Layout *** #
        
        LEFT_BOTTOM = wx.ALIGN_LEFT|wx.ALIGN_BOTTOM
        LEFT_CENTER = wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL
        RIGHT_CENTER = wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL
        
        lyt_info = wx.FlexGridSizer(2, 6)
        
        lyt_info.AddGrowableCol(1)
        lyt_info.AddGrowableCol(3)
        lyt_info.AddGrowableCol(5)
        lyt_info.AddMany((
            (txt_package, 0, RIGHT_CENTER|wx.RIGHT, 5),
            (self.ti_package, 1, wx.EXPAND|wx.BOTTOM|wx.RIGHT, 5),
            (txt_version, 0, RIGHT_CENTER|wx.RIGHT, 5),
            (self.ti_version, 1, wx.EXPAND|wx.BOTTOM|wx.RIGHT, 5),
            (txt_dist, 0, RIGHT_CENTER|wx.RIGHT, 5),
            (self.ti_dist, 1, wx.EXPAND|wx.BOTTOM, 5),
            (txt_urgency, 0, RIGHT_CENTER|wx.RIGHT, 5),
            (self.sel_urgency, 1, wx.RIGHT, 5),
            (txt_maintainer, 0, RIGHT_CENTER|wx.RIGHT, 5),
            (self.ti_maintainer, 1, wx.EXPAND|wx.RIGHT, 5),
            (txt_email, 0, RIGHT_CENTER|wx.RIGHT, 5),
            (self.ti_email, 1, wx.EXPAND)
            ))
        
        lyt_details = wx.GridBagSizer()
        lyt_details.SetCols(3)
        lyt_details.AddGrowableRow(2)
        lyt_details.AddGrowableCol(1)
        
        lyt_details.Add(btn_import, (0, 0))
        lyt_details.Add(txt_import, (0, 1), flag=LEFT_CENTER)
        lyt_details.Add(wx.StaticText(self, label=GT(u'Changes')), (1, 0), flag=LEFT_BOTTOM)
        lyt_details.Add(wx.StaticText(self, label=GT(u'Target')), (1, 2), flag=LEFT_BOTTOM)
        lyt_details.Add(self.ti_changes, (2, 0), (1, 2), wx.EXPAND|wx.RIGHT, 5)
        lyt_details.Add(self.pnl_target, (2, 2))
        lyt_details.Add(self.btn_add, (3, 0), (2, 1))
        lyt_details.Add(txt_add, (3, 1), flag=LEFT_BOTTOM|wx.TOP, border=5)
        lyt_details.Add(self.chk_indentation, (4, 1), flag=LEFT_BOTTOM)
        
        lyt_main = BoxSizer(wx.VERTICAL)
        lyt_main.AddSpacer(10)
        lyt_main.Add(lyt_info, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        lyt_main.AddSpacer(10)
        lyt_main.Add(lyt_details, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        lyt_main.Add(wx.StaticText(self, label=u'Changelog Output'),
                0, LEFT_BOTTOM|wx.LEFT|wx.TOP, 5)
        lyt_main.Add(self.dsp_changes, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
    
    
    ## TODO: Doxygen
    def AddInfo(self, event=None):
        new_changes = self.ti_changes.GetValue()
        
        if TextIsEmpty(new_changes):
            DetailedMessageDialog(GetMainWindow(), GT(u'Warning'), ICON_WARNING,
                    GT(u'"Changes" section is empty')).ShowModal()
            
            self.ti_changes.SetInsertionPointEnd()
            self.ti_changes.SetFocus()
            
            return
        
        package = self.ti_package.GetValue()
        version = self.ti_version.GetValue()
        dist = self.ti_dist.GetValue()
        urgency = self.sel_urgency.GetStringSelection()
        maintainer = self.ti_maintainer.GetValue()
        email = self.ti_email.GetValue()
        
        new_changes = FormatChangelog(new_changes, package, version, dist, urgency,
                maintainer, email, self.chk_indentation.GetValue())
        
        # Clean up leading & trailing whitespace in old changes
        old_changes = self.dsp_changes.GetValue().strip(u' \t\n\r')
        
        # Only append newlines if log isn't already empty
        if not TextIsEmpty(old_changes):
            new_changes = u'{}\n\n\n{}'.format(new_changes, old_changes)
        
        # Add empty line to end of log
        if not new_changes.endswith(u'\n'):
            new_changes = u'{}\n'.format(new_changes)
        
        self.dsp_changes.SetValue(new_changes)
        
        # Clear "Changes" text
        self.ti_changes.Clear()
        self.ti_changes.SetFocus()
    
    
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
        target = self.pnl_target.GetPath()
        
        if target == self.pnl_target.GetDefaultPath():
            target.replace(u'<package>', GetFieldValue(pgid.CONTROL, inputid.PACKAGE))
        
        stage = ConcatPaths((stage, target))
        
        if not os.path.isdir(stage):
            os.makedirs(stage)
        
        # FIXME: Allow user to set filename
        self.Export(stage, u'changelog', True)
        
        export_summary = GT(u'Changelog export failed')
        changelog = ConcatPaths((stage, u'changelog.gz'))
        
        if os.path.isfile(changelog):
            export_summary = GT(u'Changelog export to: {}').format(changelog)
        
        return(0, export_summary)
    
    
    ## Retrieves changelog information
    #  
    #  The output is a text file that uses sections defined
    #    by braces ([, ]).
    #  \return
    #        \b \e tuple(str, str) : Filename & formatted string of changelog target & body
    def Get(self, getModule=False):
        target = self.pnl_target.GetPath()
        
        if target == self.pnl_target.GetDefaultPath():
            target = u'DEFAULT'
        
        body = self.dsp_changes.GetValue()
        
        if TextIsEmpty(body):
            page = None
        
        else:
            page = u'[TARGET={}]\n\n[BODY]\n{}'.format(target, body)
        
        if getModule:
            page = (__name__, page,)
        
        return page
    
    
    ## TODO: Doxygen
    def GetChangelog(self):
        return self.dsp_changes.GetValue()
    
    
    ## TODO: Doxygen
    def ImportFromFile(self, filename):
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
                    
                    if not self.pnl_target.UsingDefault():
                        self.pnl_target.Reset()
                
                else:
                    Logger.Debug(__name__, GT(u'Using custom target: {}').format(sections[S][0]))
                    
                    self.pnl_target.SetPath(sections[S][0])
                
                continue
            
            if S == u'BODY':
                Logger.Debug(__name__, u'SECTION BODY FOUND')
                
                self.dsp_changes.SetValue(sections[S])
                
                continue
        
        return 0
    
    
    ## TODO: Doxygen
    def IsOkay(self):
        return not TextIsEmpty(self.dsp_changes.GetValue())
    
    
    ## TODO: Doxygen
    def OnImportFromControl(self, event=None):
        fields = (
            (self.ti_package, inputid.PACKAGE),
            (self.ti_version, inputid.VERSION),
            (self.ti_maintainer, inputid.MAINTAINER),
            (self.ti_email, inputid.EMAIL),
            )
        
        for F, FID in fields:
            field_value = GetFieldValue(pgid.CONTROL, FID)
            
            if isinstance(field_value, ErrorTuple):
                err_msg1 = GT(u'Got error when attempting to retrieve field value')
                err_msg2 = u'\tError code: {}\n\tError message: {}'.format(field_value.GetCode(), field_value.GetString())
                Logger.Error(__name__, u'{}:\n{}'.format(err_msg1, err_msg2))
                
                continue
            
            if not TextIsEmpty(field_value):
                F.SetValue(field_value)
    
    
    ## TODO: Doxygen
    def Set(self, data):
        changelog = data.split(u'\n')
        target = changelog[0].split(u'<<DEST>>')[1].split(u'<</DEST>>')[0]
        
        if target == u'DEFAULT':
            if not self.pnl_target.UsingDefault():
                self.pnl_target.Reset()
        
        else:
            self.pnl_target.SetPath(target)
        
        self.dsp_changes.SetValue(u'\n'.join(changelog[1:]))
