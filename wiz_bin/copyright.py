# -*- coding: utf-8 -*-

## \package wiz_bin.copyright

# MIT licensing
# See: docs/LICENSE.txt


import wx

from dbr.functions      import GetSystemLicensesList
from dbr.functions      import TextIsEmpty
from dbr.language       import GT
from globals.ident      import ID_COPYRIGHT
from globals.tooltips   import SetPageToolTips


## Copyright page
class Panel(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, ID_COPYRIGHT, name=GT(u'Copyright'))
        
        self.SetScrollbars(0, 20, 0, 0)
        
        opts_licenses = GetSystemLicensesList()
        for O in opts_licenses:
            print(u'System license: {}'.format(O))
        
        btn_template = wx.Button(self, label=GT(u'Generate Template'), name=u'full')
        
        self.sel_templates = wx.Choice(self, choices=opts_licenses, name=u'list')
        self.sel_templates.SetSelection(0)
        
        template_sizer = wx.BoxSizer(wx.HORIZONTAL)
        template_sizer.Add(btn_template, 1)
        template_sizer.Add(self.sel_templates, 1)
        
        self.dsp_copyright = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        
        SetPageToolTips(self)
        
        # *** Layout *** #
        
        lyt_main = wx.BoxSizer(wx.VERTICAL)
        lyt_main.Add(template_sizer, 0, wx.ALL, 5)
        lyt_main.Add(self.dsp_copyright, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(lyt_main)
        self.Layout()
        
        # *** Event handlers *** #
        
        btn_template.Bind(wx.EVT_BUTTON, self.GenerateTemplate)
    
    
    ## TODO: Doxygen
    def DestroyLicenseText(self):
        main_window = wx.GetApp().GetTopWindow()
        
        empty = TextIsEmpty(self.dsp_copyright.GetValue())
        
        if not empty:
            if wx.MessageDialog(main_window,
                    GT(u'This will destroy all license text. Do you want to continue?'),
                    GT(u'Warning'),
                    wx.YES_NO|wx.NO_DEFAULT|wx.ICON_EXCLAMATION).ShowModal() == wx.ID_NO:
                return 0
        
        return 1
    
    
    ## TODO: Doxygen
    def GatherData(self):
        data = self.GetCopyright()
        return u'<<COPYRIGHT>>\n{}\n<</COPYRIGHT>>'.format(data)
    
    
    ## TODO: Doxygen
    def GenerateTemplate(self, event=None):
        if not self.DestroyLicenseText():
            return
        
        self.dsp_copyright.Clear()
        
        lic_path = u'/usr/share/common-licenses/{}'.format(self.sel_templates.GetStringSelection())
        cpright = u'Copyright: <year> <copyright holder> <email>'
        
        self.dsp_copyright.SetValue(u'{}\n\n{}'.format(cpright, lic_path))
    
    
    ## TODO: Doxygen
    def GetCopyright(self):
        return self.dsp_copyright.GetValue()
    
    
    ## TODO: Doxygen
    def ResetAllFields(self):
        self.dsp_copyright.Clear()
    
    
    ## TODO: Doxygen
    def SetCopyright(self, data):
        self.dsp_copyright.SetValue(data)
