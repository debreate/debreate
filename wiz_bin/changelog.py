# -*- coding: utf-8 -*-

## \package wiz_bin.changelog


# MIT licensing
# See: docs/LICENSE.txt


import commands, wx

from dbr.buttons            import ButtonAdd
from dbr.buttons            import ButtonImport
from dbr.functions          import TextIsEmpty
from dbr.language           import GT
from dbr.log                import Logger
from dbr.pathctrl           import PATH_WARN
from dbr.pathctrl           import PathCtrl
from globals.ident          import FID_EMAIL
from globals.ident          import FID_MAINTAINER
from globals.ident          import FID_NAME
from globals.ident          import FID_VERSION
from globals.ident          import ID_CHANGELOG
from globals.ident          import ID_CONTROL
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import ErrorTuple
from globals.wizardhelper   import GetFieldValue


## Changelog page
class Panel(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, ID_CHANGELOG, name=GT(u'Changelog'))
        
        self.SetScrollbars(0, 20, 0, 0)
        
        txt_package = wx.StaticText(self, label=GT(u'Package'), name=u'package')
        self.ti_package = wx.TextCtrl(self, name=txt_package.Name)
        
        txt_version = wx.StaticText(self, label=GT(u'Version'), name=u'version')
        self.ti_version = wx.TextCtrl(self, name=txt_version.Name)
        
        txt_dist = wx.StaticText(self, label=GT(u'Distribution'), name=u'dist')
        self.ti_dist = wx.TextCtrl(self, name=txt_dist.Name)
        
        opts_urgency = (
            u'low', u'high',
            )
        
        txt_urgency = wx.StaticText(self, label=GT(u'Urgency'), name=u'urgency')
        self.sel_urgency = wx.Choice(self, choices=opts_urgency, name=txt_urgency.Name)
        self.sel_urgency.default = 0
        self.sel_urgency.SetSelection(self.sel_urgency.default)
        
        txt_maintainer = wx.StaticText(self, label=GT(u'Maintainer'), name=u'maintainer')
        self.ti_maintainer = wx.TextCtrl(self, name=txt_maintainer.Name)
        
        txt_email = wx.StaticText(self, label=GT(u'Email'), name=u'email')
        self.ti_email = wx.TextCtrl(self, name=txt_email.Name)
        
        self.button_import = ButtonImport(self)
        self.button_import.SetName(u'import')
        txt_import = wx.StaticText(self, label=GT(u'Import information from Control page'))
        
        # Changes input
        self.ti_changes = wx.TextCtrl(self, size=(20,150), style=wx.TE_MULTILINE, name=u'changes')
        
        # *** Target installation directory
        
        pnl_target = wx.Panel(self, style=wx.BORDER_THEME)
        
        # Standard destination of changelog
        self.rb_target_standard = wx.RadioButton(pnl_target, label=u'/usr/share/doc/<package>',
                name=u'target default', style=wx.RB_GROUP)
        self.rb_target_standard.default = True
        self.rb_target_standard.SetValue(self.rb_target_standard.default)
        
        # Custom destination of changelog
        # FIXME: Should not use same name as default destination???
        self.rb_target_custom = wx.RadioButton(pnl_target, name=self.rb_target_standard.Name)
        
        self.ti_target = PathCtrl(pnl_target, -1, u'/', PATH_WARN)
        self.ti_target.SetName(u'target custom')
        
        self.button_add = ButtonAdd(self)
        self.button_add.SetName(u'add')
        txt_add = wx.StaticText(self, label=GT(u'Insert new changelog entry'))
        
        self.dsp_changes = wx.TextCtrl(self, name=u'log', style=wx.TE_MULTILINE)
        
        SetPageToolTips(self)
        
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
        
        lyt_target_custom = wx.BoxSizer(wx.HORIZONTAL)
        
        lyt_target_custom.Add(self.rb_target_custom, 0, wx.ALIGN_CENTER_VERTICAL)
        lyt_target_custom.Add(self.ti_target, 1)
        
        lyt_target = wx.BoxSizer(wx.VERTICAL)
        
        lyt_target.AddSpacer(5)
        lyt_target.Add(self.rb_target_standard)
        lyt_target.AddSpacer(5)
        lyt_target.Add(lyt_target_custom, 0, wx.EXPAND)
        lyt_target.AddSpacer(5)
        
        pnl_target.SetSizer(lyt_target)
        pnl_target.SetAutoLayout(True)
        pnl_target.Layout()
        
        LEFT_BOTTOM = wx.ALIGN_LEFT|wx.ALIGN_BOTTOM
        LEFT_CENTER = wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL
        
        lyt_details = wx.GridBagSizer()
        lyt_details.SetCols(3)
        lyt_details.AddGrowableCol(1)
        
        lyt_details.Add(self.button_import, (0, 0))
        lyt_details.Add(txt_import, (0, 1), flag=LEFT_CENTER)
        lyt_details.Add(wx.StaticText(self, label=GT(u'Changes')), (1, 0), flag=LEFT_BOTTOM)
        lyt_details.Add(wx.StaticText(self, label=GT(u'Target')), (1, 2), flag=LEFT_BOTTOM)
        lyt_details.Add(self.ti_changes, (2, 0), (1, 2), wx.EXPAND|wx.RIGHT, 5)
        lyt_details.Add(pnl_target, (2, 2))
        lyt_details.Add(self.button_add, (3, 0))
        lyt_details.Add(txt_add, (3, 1), flag=LEFT_CENTER)
        
        lyt_main = wx.StaticBoxSizer(wx.StaticBox(self), wx.VERTICAL)
        
        lyt_main.AddSpacer(10)
        lyt_main.Add(lyt_info, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        lyt_main.AddSpacer(10)
        lyt_main.Add(lyt_details, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        lyt_main.Add(wx.StaticText(self, label=u'Changelog Output'),
                0, wx.ALIGN_BOTTOM|wx.LEFT, 5)
        lyt_main.Add(self.dsp_changes, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        lyt_main.AddSpacer(5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Event handlers *** #
        
        self.button_import.Bind(wx.EVT_BUTTON, self.OnImportFromControl)
        self.button_add.Bind(wx.EVT_BUTTON, self.AddInfo)
    
    
    ## TODO: Doxygen
    def AddInfo(self, event=None):
        package = self.ti_package.GetValue()
        version = self.ti_version.GetValue()
        distribution = self.ti_dist.GetValue()
        urgency = self.sel_urgency.GetStringSelection()
        info1 = u'{} ({}) {}; urgency={}'.format(package, version, distribution, urgency)
        
        details = []
        for line in self.ti_changes.GetValue().split(u'\n'):
            if line == self.ti_changes.GetValue().split(u'\n')[0]:
                line = u'  * {}'.format(line)
            
            else:
                line = u'    {}'.format(line)
            
            details.append(line)
        
        details.insert(0, wx.EmptyString)
        details.append(wx.EmptyString)
        details = u'\n'.join(details)
        
        maintainer = self.ti_maintainer.GetValue()
        email = self.ti_email.GetValue()
        # FIXME: Use GetDate method
        date = commands.getoutput(u'date -R')
        info2 = u' -- {} <{}>  {}'.format(maintainer, email, date)
        
        entry = u'\n'.join((info1, details, info2))
        self.dsp_changes.SetValue(u'\n'.join((entry, wx.EmptyString, self.dsp_changes.GetValue())))
    
    
    ## TODO: Doxygen
    def GatherData(self):
        if self.rb_target_standard.GetValue():
            dest = u'<<DEST>>DEFAULT<</DEST>>'
        
        elif self.rb_target_custom.GetValue():
            dest = u'<<DEST>>' + self.ti_target.GetValue() + u'<</DEST>>'
        
        return u'\n'.join((u'<<CHANGELOG>>', dest, self.dsp_changes.GetValue(), u'<</CHANGELOG>>'))
    
    
    ## TODO: Doxygen.
    def GetChangelog(self):
        return self.dsp_changes.GetValue()
    
    
    ## TODO: Doxygen
    def OnImportFromControl(self, event=None):
        fields = (
            (self.ti_package, FID_NAME),
            (self.ti_version, FID_VERSION),
            (self.ti_maintainer, FID_MAINTAINER),
            (self.ti_email, FID_EMAIL),
            )
        
        for F, FID in fields:
            field_value = GetFieldValue(ID_CONTROL, FID)
            
            if isinstance(field_value, ErrorTuple):
                err_msg1 = GT(u'Got error when attempting to retrieve field value')
                err_msg2 = u'\tError code: {}\n\tError message: {}'.format(field_value.GetCode(), field_value.GetString())
                Logger.Error(__name__, u'{}:\n{}'.format(err_msg1, err_msg2))
                
                continue
            
            if not TextIsEmpty(field_value):
                F.SetValue(field_value)
    
    
    ## TODO: Doxygen
    def ResetAllFields(self):
        self.ti_package.Clear()
        self.ti_version.Clear()
        self.ti_dist.Clear()
        self.sel_urgency.SetSelection(self.sel_urgency.default)
        self.ti_maintainer.Clear()
        self.ti_email.Clear()
        self.ti_changes.Clear()
        self.rb_target_standard.SetValue(self.rb_target_standard.default)
        self.ti_target.SetValue(u'/')
        self.dsp_changes.Clear()
    
    
    ## TODO: Doxygen
    def SetChangelog(self, data):
        changelog = data.split(u'\n')
        dest = changelog[0].split(u'<<DEST>>')[1].split(u'<</DEST>>')[0]
        
        if dest == u'DEFAULT':
            self.rb_target_standard.SetValue(True)
        
        else:
            self.rb_target_custom.SetValue(True)
            self.ti_target.SetValue(dest)
        
        self.dsp_changes.SetValue(u'\n'.join(changelog[1:]))
