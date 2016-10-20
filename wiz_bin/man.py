# -*- coding: utf-8 -*-

import wx

from dbr.language   import GT
from dbr.wizard     import  WizardPage
from globals.ident import ID_MAN
from globals.tooltips import SetPageToolTips
from dbr.buttons import ButtonAdd


class Panel(WizardPage, wx.Notebook):
    def __init__(self, parent):
        # TODO: Add to Gettext locale files
        WizardPage.__init__(self, parent, ID_MAN)
        
        ## Override default label
        self.label = GT(u'Manpages')
        
        button_add = ButtonAdd(self)
        button_add.SetName(u'add')
        
        wx.EVT_BUTTON(button_add, wx.ID_ANY, self.OnAddManpage)
        
        self.tabs = wx.Notebook(self)
        
        layout_V1 = wx.BoxSizer(wx.VERTICAL)
        layout_V1.Add(button_add, 0, wx.ALL, 5)
        layout_V1.Add(self.tabs, 1, wx.ALL|wx.EXPAND, 5)
        
        self.SetAutoLayout(True)
        self.SetSizer(layout_V1)
        self.Layout()
        
        
        SetPageToolTips(self)
    
    
    def AddManpage(self, name=u'manual'):
        newman = ManPage(self.tabs, name)
        self.tabs.AddPage(newman, name)
    
    
    def OnAddManpage(self, event=None):
        getname = wx.TextEntryDialog(self.debreate, GT(u'Name for new manpage'))
        
        # FIXME: Better way to do this?
        invalid_name = True
        while invalid_name:
            if getname.ShowModal() == wx.ID_OK:
                name = getname.GetValue()
                invalid_name = False
                
                # FIXME: support unicode characters
                for C in name:
                    if not C.isalnum():
                        invalid_name = True
                        wx.MessageDialog(self.debreate, GT(u'Invalid characters found in name'), GT(u'Error'),
                            style=wx.OK|wx.ICON_ERROR).ShowModal()
                        break
                
                if not invalid_name:
                    self.AddManpage(name)
            
            invalid_name = False
    
    
    ## Retrieves manpages info for text output
    #  
    #  TODO: Nothing here yet
    def GetPageInfo(self):
        return wx.EmptyString
    
    
    def ImportPageInfo(self, filename):
        pass
    
    
    def ResetPageInfo(self):
        pass



class ManPage(wx.NotebookPage):
    def __init__(self, parent, name=u'manual'):
        wx.NotebookPage.__init__(self, parent, name=name)
        
        self.parent = parent
        
        # List of sections & definitions
        self.sections = {
            u'1': GT(u'General commands'),
            u'2': GT(u'System calls'),
            u'3': GT(u'Library functions'),
            u'4': GT(u'Special files and drivers'),
            u'5': GT(u'File formats and conventions'),
            u'6': GT(u'Games and screensavers'),
            u'7': GT(u'Miscellanea'),
            u'8': GT(u'System administration commands and daemons'),
        }
        
        self.bg = wx.Panel(self)
        
        section_title = wx.StaticText(self.bg, label=GT(u'Section'))
        
        self.section = wx.Choice(self.bg, choices=tuple(self.sections))
        self.section.default = u'1'
        self.section.SetStringSelection(self.section.default)
        
        self.section_definition = wx.StaticText(self.bg, label=self.sections[self.section.default])
        
        wx.EVT_CHOICE(self.section, wx.ID_ANY, self.OnSetSection)
        
        layout_H1 = wx.BoxSizer(wx.HORIZONTAL)
        layout_H1.Add(section_title, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER, 5)
        layout_H1.Add(self.section, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER, 5)
        layout_H1.Add(self.section_definition, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER, 5)
        
        self.man_text = wx.TextCtrl(self.bg, style=wx.TE_MULTILINE)
        
        layout_V1 = wx.BoxSizer(wx.VERTICAL)
        layout_V1.Add(layout_H1, 0, wx.TOP|wx.BOTTOM, 5)
        layout_V1.Add(self.man_text, 1, wx.ALL|wx.EXPAND, 5)
        
        self.bg.SetAutoLayout(True)
        self.bg.SetSizer(layout_V1)
        self.bg.Layout()
    
    
    def OnSetSection(self, event=None):
        self.section_definition.SetLabel(self.sections[self.section.GetStringSelection()])
        print(u'Setting section to {}'.format(self.section.GetStringSelection()))
