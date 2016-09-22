# -*- coding: utf-8 -*-


import commands
from wx import \
	ALIGN_CENTER_VERTICAL as wxALIGN_CENTER_VERTICAL, \
	ALIGN_RIGHT as wxALIGN_RIGHT, \
	BOTTOM as wxBOTTOM, \
	EXPAND as wxEXPAND, \
	HORIZONTAL as wxHORIZONTAL, \
	LEFT as wxLEFT, \
	RB_GROUP as wxRB_GROUP, \
	RIGHT as wxRIGHT, \
	TE_MULTILINE as wxTE_MULTILINE, \
	TOP as wxTOP, \
	VERTICAL as wxVERTICAL, \
	EVT_BUTTON as wxEVT_BUTTON
from wx import \
	BoxSizer as wxBoxSizer, \
	Choice as wxChoice, \
	EmptyString as wxEmptyString, \
	FlexGridSizer as wxFlexGridSizer, \
	Panel as wxPanel, \
	RadioButton as wxRadioButton, \
	StaticBox as wxStaticBox, \
	StaticBoxSizer as wxStaticBoxSizer, \
	StaticText as wxStaticText, \
	TextCtrl as wxTextCtrl, \
	ToolTip as wxToolTip, \
	NewId as wxNewId

import dbr


ID = wxNewId()

class Panel(wxPanel):
    def __init__(self, parent, id=ID, name=_(u'Changelog')):
        wxPanel.__init__(self, parent, id, name=_(u'Changelog'))
        
        self.parent = parent.parent # MainWindow
        
        self.package_text = wxStaticText(self, -1, _(u'Package'))
        self.package = wxTextCtrl(self)
        self.version_text = wxStaticText(self, -1, _(u'Version'))
        self.version = wxTextCtrl(self)
        self.distribution_text = wxStaticText(self, -1, _(u'Distribution'))
        self.distribution = wxTextCtrl(self)
        self.urgency_text = wxStaticText(self, -1, _(u'Urgency'))
        self.urgency_opt = (u'low', u'HIGH')
        self.urgency = wxChoice(self, choices=self.urgency_opt)
        self.maintainer_text = wxStaticText(self, -1, _(u'Maintainer'))
        self.maintainer = wxTextCtrl(self)
        self.email_text = wxStaticText(self, -1, _(u'Email'))
        self.email = wxTextCtrl(self)
        
        info_sizer = wxFlexGridSizer(2, 6, 5, 5)
        info_sizer.AddGrowableCol(1)
        info_sizer.AddGrowableCol(3)
        info_sizer.AddGrowableCol(5)
        info_sizer.AddMany([
            (self.package_text, 0, wxALIGN_CENTER_VERTICAL|wxALIGN_RIGHT), (self.package, 1, wxEXPAND),
            (self.version_text, 0, wxALIGN_CENTER_VERTICAL|wxALIGN_RIGHT), (self.version, 1, wxEXPAND),
            (self.distribution_text, 0, wxALIGN_CENTER_VERTICAL|wxALIGN_RIGHT), (self.distribution, 1, wxEXPAND),
            (self.urgency_text, 0, wxALIGN_CENTER_VERTICAL|wxALIGN_RIGHT), (self.urgency, 1, wxEXPAND),
            (self.maintainer_text, 0, wxALIGN_CENTER_VERTICAL|wxALIGN_RIGHT), (self.maintainer, 1, wxEXPAND),
            (self.email_text, 0, wxALIGN_CENTER_VERTICAL|wxALIGN_RIGHT), (self.email, 1, wxEXPAND)
            ])
        
        # *** CHANGES DETAILS
        self.changes = wxTextCtrl(self, size=(20,150), style=wxTE_MULTILINE)
        
        self.border_changes = wxStaticBox(self, -1, _(u'Changes'), size=(20,20))
        changes_box = wxStaticBoxSizer(self.border_changes, wxVERTICAL)
        changes_box.Add(self.changes, 1, wxEXPAND|wxTOP|wxBOTTOM, 5)
        
        # Destination of changelog
        self.rb_dest_default = wxRadioButton(self, -1, u'/usr/share/doc/%project_name%', style=wxRB_GROUP)
        self.rb_dest_custom = wxRadioButton(self)
        self.dest_custom = dbr.PathCtrl(self, -1, u'/', dbr.PATH_WARN)
        
        dest_custom_sizer = wxBoxSizer(wxHORIZONTAL)
        dest_custom_sizer.Add(self.rb_dest_custom)
        dest_custom_sizer.Add(self.dest_custom, 1)
        
        border_dest = wxStaticBox(self, -1, _(u'Target'))
        dest_box = wxStaticBoxSizer(border_dest, wxVERTICAL)
        dest_box.AddSpacer(5)
        dest_box.Add(self.rb_dest_default)
        dest_box.AddSpacer(5)
        dest_box.Add(dest_custom_sizer, 0, wxEXPAND)
        dest_box.AddSpacer(5)
        
        details_sizer = wxBoxSizer(wxHORIZONTAL)
        details_sizer.Add(changes_box, 1, wxEXPAND|wxRIGHT, 5)
        details_sizer.Add(dest_box)
        
        
        self.button_import = dbr.ButtonImport(self)
        self.button_import.SetToolTip(wxToolTip(_(u'Import information from Control section')))
        self.button_add = dbr.ButtonAdd(self)
        
        wxEVT_BUTTON(self.button_import, -1, self.ImportInfo)
        wxEVT_BUTTON(self.button_add, -1, self.AddInfo)
        
        button_sizer = wxBoxSizer(wxHORIZONTAL)
        button_sizer.Add(self.button_import)
        button_sizer.Add(self.button_add)
        
        self.display_area = wxTextCtrl(self, -1, style=wxTE_MULTILINE)
        
        # *** Widgets that Enable/Disable
#        self.toggle_list = (
#            self.package, self.version, self.distribution, self.urgency, self.maintainer, self.email,
#            self.changes, self.rb_dest_default, self.rb_dest_custom, self.dest_custom,
#            self.button_import, self.button_add, self.display_area
#            )
        
        # *** LAYOUT
        main_sizer = wxStaticBoxSizer(wxStaticBox(self), wxVERTICAL)
        main_sizer.AddSpacer(10)
        main_sizer.Add(info_sizer, 0, wxEXPAND|wxLEFT|wxRIGHT, 5)
        main_sizer.AddSpacer(10)
        main_sizer.Add(details_sizer, 0, wxEXPAND|wxLEFT|wxRIGHT, 5)
        main_sizer.Add(button_sizer, 0, wxLEFT|wxRIGHT, 5)
        main_sizer.Add(self.display_area, 1, wxEXPAND, wxLEFT|wxRIGHT, 5)
        main_sizer.AddSpacer(5)
        
        self.SetAutoLayout(True)
        self.SetSizer(main_sizer)
        self.Layout()
    
    
    def ImportInfo(self, event):
        # Import package name and version from the control page
        self.package.SetValue(self.parent.page_control.pack.GetValue())
        self.version.SetValue(self.parent.page_control.ver.GetValue())
        self.maintainer.SetValue(self.parent.page_control.auth.GetValue())
        self.email.SetValue(self.parent.page_control.email.GetValue())
    
    def AddInfo(self, event):
        package = self.package.GetValue()
        version = self.version.GetValue()
        distribution = self.distribution.GetValue()
        urgency = self.urgency_opt[self.urgency.GetSelection()]
        info1 = u'%s (%s) %s; urgency=%s' % (package, version, distribution, urgency)
        
        details = []
        for line in self.changes.GetValue().split(u'\n'):
            if line == self.changes.GetValue().split(u'\n')[0]:
                line = u'  * %s' % line
            else:
                line = u'    %s' % line
            details.append(line)
        details.insert(0, wxEmptyString)
        details.append(wxEmptyString)
        details = u'\n'.join(details)
        
        maintainer = self.maintainer.GetValue()
        email = self.email.GetValue()
        #date = commands.getoutput("date +\"%a, %d %b %Y %T %z\"")
        # FIXME: Use methods from dbr.functions to get date & time
        date = commands.getoutput(u'date -R')
        info2 = u' -- %s <%s>  %s' % (maintainer, email, date)
        
        entry = u'\n'.join((info1, details, info2))
        self.display_area.SetValue(u'\n'.join((entry, wxEmptyString, self.display_area.GetValue())))
    
    def GetChangelog(self):
        return self.display_area.GetValue()

    def SetChangelog(self, data):
        changelog = data.split(u'\n')
        dest = changelog[0].split(u'<<DEST>>')[1].split(u'<</DEST>>')[0]
        if dest == u'DEFAULT':
            self.rb_dest_default.SetValue(True)
        else:
            self.rb_dest_custom.SetValue(True)
            self.dest_custom.SetValue(dest)
        self.display_area.SetValue(u'\n'.join(changelog[1:]))
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
        self.rb_dest_default.SetValue(True)
        self.dest_custom.SetValue(u'/')
        self.display_area.Clear()
    
    def GatherData(self):
        if self.rb_dest_default.GetValue():
            dest = u'<<DEST>>DEFAULT<</DEST>>'
        elif self.rb_dest_custom.GetValue():
            dest = u'<<DEST>>' + self.dest_custom.GetValue() + u'<</DEST>>'
        
        return u'\n'.join((u'<<CHANGELOG>>', dest, self.display_area.GetValue(), u'<</CHANGELOG>>'))
