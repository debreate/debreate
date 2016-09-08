# -*- coding: utf-8 -*-

from wximports import wxNewId, wxPanel, wxStaticText, wxHyperlinkCtrl, wxStaticBox, wxGridSizer, \
	wxALIGN_CENTER, wxALIGN_CENTER_VERTICAL, wxStaticBoxSizer, wxVERTICAL, wxEXPAND, wxALL

ID = wxNewId()

class Panel(wxPanel):
    def __init__(self, parent, id=ID, name=_('Information')):
        wxPanel.__init__(self, parent, id, name=_('Information'))
        
        self.parent = parent # 3rd level) Allows executing 2st level methods
        
        # Mode Information
        m1 = _('Welcome to Debreate!')
        m2 = _('Debreate aids in building packages for installation on Debian based systems. Use the arrows located in the top-right corner or the "Page" menu to navigate through the program. For some information on Debian packages use the reference links in the "Help" menu.')
        m3 = _('For a video tutorial check the link below.')
        self.txt_bin = '%s\n\n%s\n\n%s' % (m1, m2, m3)
        self.txt_src = "This mode is not fully functional"
        self.txt_upd = "This mode is not fully functional"
        
        self.mode_info = (
            (0, "Build Package from Precompiled Files", self.txt_bin),
            (1, "Build Debian Source Package", self.txt_src),
            (2, "Update a Package", self.txt_upd)
            )
        
        # ----- Helpful information to be displayed about each mode
        self.info = wxStaticText(self, -1)
        self.vidlink = wxHyperlinkCtrl(self, -1, _('Building a Debian Package with Debreate'), 'http://www.youtube.com/watch?v=kx4D5eL6HKE')
        self.info_border = wxStaticBox(self, -1, size=(100,100))
        info_box = wxGridSizer()
        info_box.Add(self.info, 1, wxALIGN_CENTER|wxALIGN_CENTER_VERTICAL)
        
        # ----- Layout
        mode_sizer = wxStaticBoxSizer(self.info_border, wxVERTICAL)
        mode_sizer.Add(info_box, 4, wxEXPAND|wxALIGN_CENTER|wxALL, 10)
        mode_sizer.Add(self.vidlink, 2, wxEXPAND|wxALIGN_CENTER)
        
        self.SetAutoLayout(True)
        self.SetSizer(mode_sizer)
        self.Layout()
        
        
    def SetInfo(self):
        self.parent.SetTitle('Testing')
        self.info.SetLabel(self.txt_bin)
        
        self.info.Wrap(600) # Keep characters within the width of the window
        
        # Refresh widget layout
        self.Layout()		