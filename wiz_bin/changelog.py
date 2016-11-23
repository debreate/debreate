# -*- coding: utf-8 -*-


import commands, wx

from dbr.buttons        import ButtonAdd
from dbr.buttons        import ButtonImport
from dbr.language       import GT
from dbr.pathctrl       import PATH_WARN
from dbr.pathctrl       import PathCtrl
from globals.ident      import ID_CHANGELOG
from globals.tooltips   import SetPageToolTips


## TODO: Doxygen
class Panel(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, ID_CHANGELOG, name=GT(u'Changelog'))
        
        self.SetScrollbars(0, 20, 0, 0)
        
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
        self.changes = wx.TextCtrl(self, size=(20,150), style=wx.TE_MULTILINE, name=u'changes')
        
        self.border_changes = wx.StaticBox(self, label=GT(u'Changes'), size=(20,20))
        changes_box = wx.StaticBoxSizer(self.border_changes, wx.VERTICAL)
        changes_box.Add(self.changes, 1, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        
        # Destination of changelog
        self.target_default = wx.RadioButton(self, label=u'/usr/share/doc/<package>',
                name=u'target default', style=wx.RB_GROUP)
        self.target_custom = wx.RadioButton(self, name=self.target_default.Name)
        self.target = PathCtrl(self, -1, u'/', PATH_WARN)
        self.target.SetName(u'target custom')
        
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
        
        self.button_add = ButtonAdd(self)
        self.button_add.SetName(u'add')
        
        wx.EVT_BUTTON(self.button_import, -1, self.ImportInfo)
        wx.EVT_BUTTON(self.button_add, -1, self.AddInfo)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.button_import)
        button_sizer.Add(self.button_add)
        
        self.log = wx.TextCtrl(self, name=u'log', style=wx.TE_MULTILINE)
        
        # *** LAYOUT
        main_sizer = wx.StaticBoxSizer(wx.StaticBox(self), wx.VERTICAL)
        main_sizer.AddSpacer(10)
        main_sizer.Add(info_sizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        main_sizer.AddSpacer(10)
        main_sizer.Add(details_sizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        main_sizer.Add(button_sizer, 0, wx.LEFT|wx.RIGHT, 5)
        main_sizer.Add(self.log, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        main_sizer.AddSpacer(5)
        
        self.SetAutoLayout(True)
        self.SetSizer(main_sizer)
        self.Layout()
        
        
        SetPageToolTips(self)
    
    
    ## TODO: Doxygen
    def AddInfo(self, event):
        package = self.package.GetValue()
        version = self.version.GetValue()
        distribution = self.distribution.GetValue()
        urgency = self.urgency_opt[self.urgency.GetSelection()]
        info1 = u'{} ({}) {}; urgency={}'.format(package, version, distribution, urgency)
        
        details = []
        for line in self.changes.GetValue().split(u'\n'):
            if line == self.changes.GetValue().split(u'\n')[0]:
                line = u'  * {}'.format(line)
            else:
                line = u'    {}'.format(line)
            details.append(line)
        details.insert(0, wx.EmptyString)
        details.append(wx.EmptyString)
        details = u'\n'.join(details)
        
        maintainer = self.maintainer.GetValue()
        email = self.email.GetValue()
        #date = commands.getoutput(u'date +"%a, %d %b %Y %T %z"')
        # A simpler way to get the date
        date = commands.getoutput(u'date -R')
        info2 = u' -- {} <{}>  {}'.format(maintainer, email, date)
        
        entry = u'\n'.join((info1, details, info2))
        self.log.SetValue(u'\n'.join((entry, wx.EmptyString, self.log.GetValue())))
    
    
    ## TODO: Doxygen
    def GatherData(self):
        if self.target_default.GetValue():
            dest = u'<<DEST>>DEFAULT<</DEST>>'
        elif self.target_custom.GetValue():
            dest = u'<<DEST>>' + self.target.GetValue() + u'<</DEST>>'
        
        return u'\n'.join((u'<<CHANGELOG>>', dest, self.log.GetValue(), u'<</CHANGELOG>>'))
    
    
    ## TODO: Doxygen.
    def GetChangelog(self):
        return self.log.GetValue()
    
    
    ## TODO: Doxygen
    def ImportInfo(self, event):
        main_window = wx.GetApp().GetTopWindow()
        
        # Import package name and version from the control page
        self.package.SetValue(main_window.page_control.pack.GetValue())
        self.version.SetValue(main_window.page_control.ver.GetValue())
        self.maintainer.SetValue(main_window.page_control.auth.GetValue())
        self.email.SetValue(main_window.page_control.email.GetValue())
    
    
    ## TODO: Doxygen
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
    
    
    ## TODO: Doxygen
    def SetChangelog(self, data):
        changelog = data.split(u'\n')
        dest = changelog[0].split(u'<<DEST>>')[1].split(u'<</DEST>>')[0]
        if dest == u'DEFAULT':
            self.target_default.SetValue(True)
        else:
            self.target_custom.SetValue(True)
            self.target.SetValue(dest)
        self.log.SetValue(u'\n'.join(changelog[1:]))
