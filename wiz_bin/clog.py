# -*- coding: utf-8 -*-


# System imports
import os, commands
import wx

import dbr
from dbr.buttons        import ButtonAdd
from dbr.buttons        import ButtonImport
from dbr.functions      import TextIsEmpty
from dbr.language       import GT
from dbr.log            import Logger
from dbr.wizard         import WizardPage
from globals.errorcodes import dbrerrno
from globals.ident      import ID_CHANGELOG
from globals.tooltips   import SetPageToolTips
from dbr.monotext       import MonospaceTextCtrl


# Local imports
class Panel(WizardPage):
    def __init__(self, parent):
        WizardPage.__init__(self, parent, ID_CHANGELOG)
        
        self.debreate = parent.parent # MainWindow
        
        self.package_text = wx.StaticText(self, label=GT(u'Package'), name=u'package')
        self.package = wx.TextCtrl(self, name=self.package_text.Name)
        
        self.version_text = wx.StaticText(self, label=GT(u'Version'), name=u'version')
        self.version = wx.TextCtrl(self, name=self.version_text.Name)
        
        self.distribution_text = wx.StaticText(self, label=GT(u'Distribution'), name=u'dist')
        self.distribution = wx.TextCtrl(self, name=self.distribution_text.Name)
        
        self.urgency_text = wx.StaticText(self, label=GT(u'Urgency'), name=u'urgency')
        self.urgency_opt = (u'low', u'high')
        self.urgency = wx.Choice(self, choices=self.urgency_opt, name=self.urgency_text.Name)
        self.urgency.SetSelection(0)
        
        self.maintainer_text = wx.StaticText(self, label=GT(u'Maintainer'), name=u'maintainer')
        self.maintainer = wx.TextCtrl(self, name=self.maintainer_text.Name)
        
        self.email_text = wx.StaticText(self, label=GT(u'Email'), name=u'email')
        self.email = wx.TextCtrl(self, name=self.email_text.Name)
        
        info_sizer = wx.FlexGridSizer(2, 6, 5, 5)
        info_sizer.AddGrowableCol(1)
        info_sizer.AddGrowableCol(3)
        info_sizer.AddGrowableCol(5)
        info_sizer.AddMany([
            (self.package_text, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (self.package, 1, wx.EXPAND),
            (self.version_text, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (self.version, 1, wx.EXPAND),
            (self.distribution_text, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (self.distribution, 1, wx.EXPAND),
            (self.urgency_text, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (self.urgency, 1, wx.EXPAND),
            (self.maintainer_text, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (self.maintainer, 1, wx.EXPAND),
            (self.email_text, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT), (self.email, 1, wx.EXPAND)
            ])
        
        # *** CHANGES DETAILS
        self.changes = wx.TextCtrl(self, size=(20,150), name=u'changes', style=wx.TE_MULTILINE)
        
        self.border_changes = wx.StaticBox(self, label=GT(u'Changes'), size=(20,20))
        changes_box = wx.StaticBoxSizer(self.border_changes, wx.VERTICAL)
        changes_box.Add(self.changes, 1, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        
        # Destination of changelog
        self.target_default = wx.RadioButton(self, label=u'/usr/share/doc/<package>',
                name=u'target', style=wx.RB_GROUP)
        self.target_custom = wx.RadioButton(self, name=self.target_default.Name)
        self.target = dbr.PathCtrl(self, -1, u'/', dbr.PATH_WARN)
        self.target.SetName(self.target_default.Name)
        
        dest_custom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        dest_custom_sizer.Add(self.target_custom)
        dest_custom_sizer.Add(self.target, 1)
        
        border_dest = wx.StaticBox(self, label=GT(u'Target'))
        dest_box = wx.StaticBoxSizer(border_dest, wx.VERTICAL)
        dest_box.AddSpacer(5)
        dest_box.Add(self.target_default)
        dest_box.AddSpacer(5)
        dest_box.Add(dest_custom_sizer, 0, wx.EXPAND)
        dest_box.AddSpacer(5)
        
        details_sizer = wx.BoxSizer(wx.HORIZONTAL)
        details_sizer.Add(changes_box, 1, wx.EXPAND|wx.RIGHT, 5)
        details_sizer.Add(dest_box)
        
        
        self.button_import = ButtonImport(self)
        self.button_import.SetName(u'import')
        #self.button_import.SetToolTip(wx.ToolTip(GT(u'Import information from Control section')))
        self.button_add = ButtonAdd(self)
        self.button_add.SetName(u'add')
        
        wx.EVT_BUTTON(self.button_import, -1, self.ImportInfo)
        wx.EVT_BUTTON(self.button_add, -1, self.AddInfo)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.button_import)
        button_sizer.Add(self.button_add)
        
        #self.log = wx.TextCtrl(self, name=u'log', style=wx.TE_MULTILINE)
        self.log = MonospaceTextCtrl(self, name=u'log')
        
        # *** Widgets that Enable/Disable
#        self.toggle_list = (
#            self.package, self.version, self.distribution, self.urgency, self.maintainer, self.email,
#            self.changes, self.target_default, self.target_custom, self.target,
#            self.button_import, self.button_add, self.log
#            )
        
        # *** LAYOUT
        main_sizer = wx.StaticBoxSizer(wx.StaticBox(self), wx.VERTICAL)
        main_sizer.AddSpacer(10)
        main_sizer.Add(info_sizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        main_sizer.AddSpacer(10)
        main_sizer.Add(details_sizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        main_sizer.Add(button_sizer, 0, wx.LEFT|wx.RIGHT, 5)
        main_sizer.Add(self.log, 1, wx.EXPAND, wx.LEFT|wx.RIGHT, 5)
        main_sizer.AddSpacer(5)
        
        self.SetAutoLayout(True)
        self.SetSizer(main_sizer)
        self.Layout()
        
        
        SetPageToolTips(self)
    
    
    def IsExportable(self):
        return not TextIsEmpty(self.log.GetValue())
    
    
    def ImportInfo(self, event):
        # Import package name and version from the control page
        # FIXME: Should use a safer method
        self.package.SetValue(self.debreate.page_control.pack.GetValue())
        self.version.SetValue(self.debreate.page_control.ver.GetValue())
        self.maintainer.SetValue(self.debreate.page_control.auth.GetValue())
        self.email.SetValue(self.debreate.page_control.email.GetValue())
    
    def AddInfo(self, event):
        changes = self.changes.GetValue()
        if TextIsEmpty(changes):
            wx.MessageDialog(self.GetDebreateWindow(), GT(u'List of changes is empty'), GT(u'Warning'),
                    style=wx.OK|wx.ICON_EXCLAMATION).ShowModal()
            return
        
        package = self.package.GetValue()
        version = self.version.GetValue()
        distribution = self.distribution.GetValue()
        urgency = self.urgency_opt[self.urgency.GetSelection()]
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
        
        maintainer = self.maintainer.GetValue()
        email = self.email.GetValue()
        #date = commands.getoutput("date +\"%a, %d %b %Y %T %z\"")
        # FIXME: Use methods from dbr.functions to get date & time
        date = commands.getoutput(u'date -R')
        info2 = u' -- %s <%s>  %s' % (maintainer, email, date)
        
        entry = u'\n'.join((info1, details, info2))
        self.log.SetValue(u'\n'.join((entry, wx.EmptyString, self.log.GetValue())))
    
    def GetChangelog(self):
        return self.log.GetValue()

    def SetChangelog(self, data):
        changelog = data.split(u'\n')
        dest = changelog[0].split(u'<<DEST>>')[1].split(u'<</DEST>>')[0]
        if dest == u'DEFAULT':
            self.target_default.SetValue(True)
        else:
            self.target_custom.SetValue(True)
            self.target.SetValue(dest)
        self.log.SetValue(u'\n'.join(changelog[1:]))
        #self.Toggle(True)
    
#    def Toggle(self, value):
#        # Enable/Disable all fields
#        for item in self.toggle_list:
#            item.Enable(value)
    
    def ResetAllFields(self):
        self.package.Clear()
        self.version.Clear()
        self.distribution.Clear()
        self.urgency.SetSelection(0)
        self.maintainer.Clear()
        self.email.Clear()
        self.changes.Clear()
        self.target_default.SetValue(True)
        self.target.SetValue(u'/')
        self.log.Clear()
    
    ## Deprecated
    #  
    #  TODO: Remove after implementing new save format
    def GatherData(self):
        if self.target_default.GetValue():
            dest = u'<<DEST>>DEFAULT<</DEST>>'
        elif self.target_custom.GetValue():
            dest = u'<<DEST>>' + self.target.GetValue() + u'<</DEST>>'
        
        return u'\n'.join((u'<<CHANGELOG>>', dest, self.log.GetValue(), u'<</CHANGELOG>>'))
    
    
    ## Retrieves changelog information
    #  
    #  The output is a text file that uses sections defined
    #    by braces ([, ]).
    #  \return
    #        \b \e tuple(str, str) : Filename & formatted string of changelog target & body
    def GetPageInfo(self):
        cl_target = u'DEFAULT'
        
        if self.target_custom.GetValue():
            cl_target = self.target.GetValue()
        
        cl_body = self.log.GetValue()
        
        if TextIsEmpty(cl_body):
            return None
        
        return (__name__, u'[TARGET={}]\n\n[BODY]\n{}'.format(cl_target, cl_body))
    
    
    def ImportPageInfo(self, filename):
        if not os.path.isfile(filename):
            return dbrerrno.ENOENT
        
        FILE = open(filename, u'r')
        clog_data = FILE.read().split(u'\n')
        FILE.close()
        
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
            self.log.SetValue(sections[u'BODY'])
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
                    
                    self.target_default.SetValue(True)
                
                else:
                    Logger.Debug(__name__, GT(u'Using custom target: {}').format(sections[S][0]))
                    
                    self.target_custom.SetValue(True)
                    self.target.SetValue(sections[S][0])
                
                continue
            
            if S == u'BODY':
                Logger.Debug(__name__, u'SECTION BODY FOUND')
                
                self.log.SetValue(sections[S])
                
                continue
        
        return 0
    
    
    def ResetPageInfo(self):
        self.target.Reset()
        self.log.Clear()
