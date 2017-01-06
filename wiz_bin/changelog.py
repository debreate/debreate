# -*- coding: utf-8 -*-

## \package wiz_bin.changelog

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.buttons            import ButtonAdd
from dbr.buttons            import ButtonImport
from dbr.dialogs            import DetailedMessageDialog
from dbr.language           import GT
from dbr.log                import Logger
from dbr.panel              import BorderedPanel
from dbr.pathctrl           import PathCtrl
from dbr.selectinput        import ComboBox
from dbr.textinput          import MonospaceTextArea
from dbr.textinput          import TextAreaPanel
from globals                import ident
from globals.bitmaps        import ICON_WARNING
from globals.changes        import FormatChangelog
from globals.strings        import TextIsEmpty
from globals.system         import GetOSDistNames
from globals.tooltips       import SetPageToolTips
from globals.wizardhelper   import ErrorTuple
from globals.wizardhelper   import GetFieldValue
from globals.wizardhelper   import GetTopWindow


## Changelog page
class Panel(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, ident.CHANGELOG, name=GT(u'Changelog'))
        
        self.SetScrollbars(0, 20, 0, 0)
        
        txt_package = wx.StaticText(self, label=GT(u'Package'), name=u'package')
        self.ti_package = wx.TextCtrl(self, name=txt_package.Name)
        
        txt_version = wx.StaticText(self, label=GT(u'Version'), name=u'version')
        self.ti_version = wx.TextCtrl(self, name=txt_version.Name)
        
        dist_names = GetOSDistNames()
        
        txt_dist = wx.StaticText(self, label=GT(u'Distribution'), name=u'dist')
        
        if dist_names:
            self.ti_dist = ComboBox(self, choices=dist_names, name=txt_dist.Name)
        
        else:
            self.ti_dist = wx.TextCtrl(self, name=txt_dist.Name)
        
        opts_urgency = (
            u'low', u'medium', u'high', u'emergency',
            )
        
        txt_urgency = wx.StaticText(self, label=GT(u'Urgency'), name=u'urgency')
        self.sel_urgency = wx.Choice(self, choices=opts_urgency, name=txt_urgency.Name)
        self.sel_urgency.default = 0
        self.sel_urgency.SetSelection(self.sel_urgency.default)
        
        txt_maintainer = wx.StaticText(self, label=GT(u'Maintainer'), name=u'maintainer')
        self.ti_maintainer = wx.TextCtrl(self, name=txt_maintainer.Name)
        
        txt_email = wx.StaticText(self, label=GT(u'Email'), name=u'email')
        self.ti_email = wx.TextCtrl(self, name=txt_email.Name)
        
        btn_import = ButtonImport(self)
        txt_import = wx.StaticText(self, label=GT(u'Import information from Control page'))
        
        # Changes input
        self.ti_changes = TextAreaPanel(self, size=(20,150), name=u'changes')
        
        # *** Target installation directory
        
        pnl_target = BorderedPanel(self)
        
        # Standard destination of changelog
        self.rb_target_standard = wx.RadioButton(pnl_target, label=u'/usr/share/doc/<package>',
                name=u'target default', style=wx.RB_GROUP)
        self.rb_target_standard.default = True
        self.rb_target_standard.SetValue(self.rb_target_standard.default)
        
        # Custom destination of changelog
        # FIXME: Should not use same name as default destination???
        self.rb_target_custom = wx.RadioButton(pnl_target, name=self.rb_target_standard.Name)
        
        self.ti_target = PathCtrl(pnl_target, value=u'/', default=u'/')
        self.ti_target.SetName(u'target custom')
        
        self.btn_add = ButtonAdd(self)
        txt_add = wx.StaticText(self, label=GT(u'Insert new changelog entry'))
        
        self.dsp_changes = MonospaceTextArea(self, name=u'log')
        self.dsp_changes.EnableDropTarget()
        
        SetPageToolTips(self)
        
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
            (self.sel_urgency, 1, wx.EXPAND|wx.RIGHT, 5),
            (txt_maintainer, 0, RIGHT_CENTER|wx.RIGHT, 5),
            (self.ti_maintainer, 1, wx.EXPAND|wx.RIGHT, 5),
            (txt_email, 0, RIGHT_CENTER|wx.RIGHT, 5),
            (self.ti_email, 1, wx.EXPAND)
            ))
        
        lyt_target_custom = wx.BoxSizer(wx.HORIZONTAL)
        
        lyt_target_custom.Add(self.rb_target_custom, 0, wx.ALIGN_CENTER_VERTICAL)
        lyt_target_custom.Add(self.ti_target, 1)
        
        lyt_target = wx.BoxSizer(wx.VERTICAL)
        
        lyt_target.AddSpacer(5)
        lyt_target.Add(self.rb_target_standard, 0, wx.RIGHT, 5)
        lyt_target.AddSpacer(5)
        lyt_target.Add(lyt_target_custom, 0, wx.EXPAND|wx.RIGHT, 5)
        lyt_target.AddSpacer(5)
        
        pnl_target.SetSizer(lyt_target)
        pnl_target.SetAutoLayout(True)
        pnl_target.Layout()
        
        lyt_details = wx.GridBagSizer()
        lyt_details.SetCols(3)
        lyt_details.AddGrowableRow(2)
        lyt_details.AddGrowableCol(1)
        
        lyt_details.Add(btn_import, (0, 0))
        lyt_details.Add(txt_import, (0, 1), flag=LEFT_CENTER)
        lyt_details.Add(wx.StaticText(self, label=GT(u'Changes')), (1, 0), flag=LEFT_BOTTOM)
        lyt_details.Add(wx.StaticText(self, label=GT(u'Target')), (1, 2), flag=LEFT_BOTTOM)
        lyt_details.Add(self.ti_changes, (2, 0), (1, 2), wx.EXPAND|wx.RIGHT, 5)
        lyt_details.Add(pnl_target, (2, 2))
        lyt_details.Add(self.btn_add, (3, 0))
        lyt_details.Add(txt_add, (3, 1), flag=LEFT_CENTER)
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.AddSpacer(10)
        lyt_main.Add(lyt_info, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        lyt_main.AddSpacer(10)
        lyt_main.Add(lyt_details, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        lyt_main.Add(wx.StaticText(self, label=u'Changelog Output'),
                0, LEFT_BOTTOM|wx.LEFT, 5)
        lyt_main.Add(self.dsp_changes, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Event handlers *** #
        
        btn_import.Bind(wx.EVT_BUTTON, self.OnImportFromControl)
        self.btn_add.Bind(wx.EVT_BUTTON, self.AddInfo)
    
    
    ## TODO: Doxygen
    def AddInfo(self, event=None):
        new_changes = self.ti_changes.GetValue()
        
        if TextIsEmpty(new_changes):
            DetailedMessageDialog(GetTopWindow(), GT(u'Warning'), ICON_WARNING,
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
                maintainer, email)
        
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
    #  
    #  \return
    #        \b \e tuple : Changelog target dir & text
    def ExportPage(self):
        target = u'STANDARD'
        if self.rb_target_custom.GetValue():
            target = self.ti_target.GetValue()
        
        return (target, self.GetChangelog())
    
    
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
    def IsBuildExportable(self):
        return not TextIsEmpty(self.dsp_changes.GetValue())
    
    
    ## TODO: Doxygen
    def OnImportFromControl(self, event=None):
        fields = (
            (self.ti_package, ident.F_PACKAGE),
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
    def ResetAllFields(self):
        self.ti_package.Clear()
        self.ti_version.Clear()
        self.ti_dist.Clear()
        self.sel_urgency.SetSelection(self.sel_urgency.default)
        self.ti_maintainer.Clear()
        self.ti_email.Clear()
        self.ti_changes.Clear()
        self.rb_target_standard.SetValue(self.rb_target_standard.default)
        self.ti_target.Reset()
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
