# -*- coding: utf-8 -*-

## \package wiz_bin.copyright


import wx

from dbr.functions      import TextIsEmpty
from dbr.language       import GT
from globals.ident      import ID_COPYRIGHT
from globals.tooltips   import SetPageToolTips


## Copyright page
class Panel(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, ID_COPYRIGHT, name=GT(u'Copyright'))
        
        self.SetScrollbars(0, 20, 0, 0)
        
        lic_options = (
            u'Apache-2.0', u'Artistic', u'BSD', u'GFDL', u'GFDL-1.2',
            u'GFDL-1.3', u'GPL', u'GPL-1', u'GPL-2', u'GPL-3', u'LGPL',
            u'LGPL-2', u'LGPL-2.1', u'LGPL-3'
        )
        
        template_btn = wx.Button(self, label=GT(u'Generate Template'), name=u'full')
        
        self.template_lic = wx.Choice(self, choices=lic_options, name=u'list')
        self.template_lic.SetSelection(0)
        
        wx.EVT_BUTTON(template_btn, -1, self.GenerateTemplate)
        
        template_sizer = wx.BoxSizer(wx.HORIZONTAL)
        template_sizer.Add(template_btn, 1)
        template_sizer.Add(self.template_lic, 1)
        
        self.cp_display = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(template_sizer, 0, wx.ALL, 5)
        main_sizer.Add(self.cp_display, 1, wx.EXPAND|wx.ALL, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(main_sizer)
        self.Layout()
        
        
        SetPageToolTips(self)
    
    
    ## TODO: Doxygen
    def DestroyLicenseText(self):
        main_window = wx.GetApp().GetTopWindow()
        
        empty = TextIsEmpty(self.cp_display.GetValue())
        
        if not empty:
            if wx.MessageDialog(main_window, GT(u'This will destroy all license text. Do you want to continue?'), GT(u'Warning'),
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
        
        self.cp_display.Clear()
        
        lic_path = u'/usr/share/common-licenses/{}'.format(self.template_lic.GetString(self.template_lic.GetSelection()))
        cpright = u'Copyright: <year> <copyright holder> <email>'
        
        self.cp_display.SetValue(u'{}\n\n{}'.format(cpright, lic_path))
    
    
    ## TODO: Doxygen
    def GetCopyright(self):
        return self.cp_display.GetValue()
    
    
    ## TODO: Doxygen
    def ResetAllFields(self):
        self.cp_display.Clear()
    
    
    ## TODO: Doxygen
    def SetCopyright(self, data):
        self.cp_display.SetValue(data)
