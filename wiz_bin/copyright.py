# -*- coding: utf-8 -*-


from wx import \
	ALL as wxALL, \
	EXPAND as wxEXPAND, \
	HORIZONTAL as wxHORIZONTAL, \
	TE_MULTILINE as wxTE_MULTILINE, \
	VERTICAL as wxVERTICAL, \
	EVT_BUTTON as wxEVT_BUTTON, \
	ID_ANY as wxID_ANY
from wx import \
	BoxSizer as wxBoxSizer, \
	Button as wxButton, \
	Choice as wxChoice, \
	NewId as wxNewId, \
	Panel as wxPanel, \
	TextCtrl as wxTextCtrl


ID = wxNewId()

class Panel(wxPanel):
    def __init__(self, parent, id=wxID_ANY):
        wxPanel.__init__(self, parent, id, name=_('Copyright'))
        
        self.debreate = parent.parent
        
        lic_options = (
        	'Apache-2.0', 'Artistic', 'BSD', 'GFDL', 'GFDL-1.2',
        	'GFDL-1.3', 'GPL', 'GPL-1', 'GPL-2', 'GPL-3', 'LGPL',
        	'LGPL-2', 'LGPL-2.1', 'LGPL-3'
        )
        template_btn = wxButton(self, -1, 'Generate Template')
        self.template_lic = wxChoice(self, -1, choices=lic_options)
        
        wxEVT_BUTTON(template_btn, -1, self.GenerateTemplate)
        
        template_sizer = wxBoxSizer(wxHORIZONTAL)
        template_sizer.Add(template_btn, 1)
        template_sizer.Add(self.template_lic, 1)
        
        self.cp_display = wxTextCtrl(self, style=wxTE_MULTILINE)
        
        main_sizer = wxBoxSizer(wxVERTICAL)
        main_sizer.Add(template_sizer, 0, wxALL, 5)
        main_sizer.Add(self.cp_display, 1, wxEXPAND|wxALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(main_sizer)
        self.Layout()
    
    def GetCopyright(self):
        return self.cp_display.GetValue()
    
    def GatherData(self):
        data = self.GetCopyright()
        return "<<COPYRIGHT>>\n%s\n<</COPYRIGHT>>" % data
    
    def SetCopyright(self, data):
        self.cp_display.SetValue(data)
    
    def ResetAllFields(self):
        self.cp_display.Clear()
    
    def GenerateTemplate(self, event):
        lic_path = '/usr/share/common-licenses/{}'.format(self.template_lic.GetString(self.template_lic.GetSelection()))
        text = ''
        if (not self.cp_display.IsEmpty()):
            text = '\n{}'.format(self.cp_display.GetValue())
            self.cp_display.Clear()
        copyright = 'Copyright: <year> <copyright holder> <email>'
        text = '{}\n\n{}\n{}'.format(copyright, lic_path, text)
        self.cp_display.SetValue(text)
