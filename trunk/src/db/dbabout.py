# -*- coding: utf-8 -*-

from common import setWXVersion, application_path
setWXVersion()

import wx, db, wx.richtext

class AboutDialog(wx.Dialog):
    """Shows information about Debreate"""
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(400,375))
        
        # Font for the name
        bigfont = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        
        # Create a tabbed interface
        tabs = wx.Notebook(self, -1)
        #tabs.SetForegroundColour((255,255,255,255))
        #tabs.SetBackgroundColour((50,50,50,50))
        
        # Pages
        about = wx.Panel(tabs, -1)
        self.about = about
        #about.SetBackgroundColour((0,0,0,0))
        credits = wx.Panel(tabs, -1)
        changelog = wx.Panel(tabs, -1)
        license = wx.Panel(tabs, -1)
        
        # Add pages to tabbed interface
        tabs.AddPage(about, _(u'About'))
        tabs.AddPage(credits, _(u'Credits'))
        tabs.AddPage(changelog, _(u'Changelog'))
        tabs.AddPage(license, _(u'License'))
        
        # Put a picture on the first page
        self.graphic = wx.StaticBitmap(about, -1, self.SetGraphic("%s/bitmaps/debreate64.png" % application_path))
        # Show the name and version of the application
        self.app = wx.StaticText(about, -1)
        self.app.SetFont(bigfont)
        # Show the author & website
        self.author = wx.StaticText(about)
        self.website = self.SetWebsite("http://debreate.sourceforge.net/")
        # Show a short description
        self.description = wx.StaticText(self, -1)
        
        about_sizer = wx.BoxSizer(wx.VERTICAL)
        about_sizer.Add(self.graphic, 0, wx.ALIGN_CENTER|wx.ALL, 10)
        about_sizer.Add(self.app, 0, wx.ALIGN_CENTER|wx.ALL, 10)
        about_sizer.Add(self.author, 0, wx.ALIGN_CENTER|wx.ALL, 10)
        about_sizer.Add(self.website, 0, wx.ALIGN_CENTER|wx.ALL, 10)
        about_sizer.Add(self.description, 1, wx.ALIGN_CENTER|wx.ALL, 10)
        
        about.SetAutoLayout(True)
        about.SetSizer(about_sizer)
        about.Layout()
        
        # Show the credits
        self.credits = wx.ListCtrl(credits, -1, style=wx.LC_REPORT)
        self.credits.InsertColumn(0, _(u'Name'), width=100)
        self.credits.InsertColumn(1, _(u'Job'), width=100)
        self.credits.InsertColumn(2, _(u'Email'), width=200)
        #self.credits.SetBackgroundColour((0,0,0,0))
        
        credits_sizer = wx.BoxSizer(wx.VERTICAL)
        credits_sizer.Add(self.credits, 1, wx.EXPAND)
        
        credits.SetAutoLayout(True)
        credits.SetSizer(credits_sizer)
        credits.Layout()
        
        # Keep users from resizing columns
        #wx.EVT_LIST_COL_BEGIN_DRAG(self.credits, wx.ID_ANY, self.NoResizeCol)
        
        # Show changelog
        self.changelog = wx.TextCtrl(changelog, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        #self.changelog.SetBackgroundColour((0,0,0,0))
        #self.changelog.SetForegroundColour((255,255,255,255))
        
        log_sizer = wx.BoxSizer(wx.VERTICAL)
        log_sizer.Add(self.changelog, 1, wx.EXPAND)
        
        changelog.SetSizer(log_sizer)
        changelog.Layout()
        
        
        # Show the license
        self.license = wx.TextCtrl(license, -1, style=wx.TE_READONLY|wx.TE_MULTILINE)
        #self.license.SetBackgroundColour((0,0,0,0))
        #self.license.SetForegroundColour((255,255,255,255))
        
        license_sizer = wx.BoxSizer(wx.VERTICAL)
        license_sizer.Add(self.license, 1, wx.EXPAND)
        
        license.SetSizer(license_sizer)
        license.Layout()
        
        
        # Button to close the dialog
        ok = db.ButtonConfirm(self)#wx.Button(self, wx.OK, "Ok")
        #wx.EVT_BUTTON(ok, wx.OK, self.OnOk)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tabs, 1, wx.EXPAND)
        sizer.Add(ok, 0, wx.ALIGN_RIGHT|wx.RIGHT|wx.TOP, 5)
        
        self.SetSizer(sizer)
        self.Layout()
    
    
    def SetGraphic(self, graphic):
        image = wx.Image(graphic)
        image.Rescale(64, 64, wx.IMAGE_QUALITY_HIGH)
        #self.graphic.SetBitmap(image.ConvertToBitmap())
        return image.ConvertToBitmap()

    def SetVersion(self, name, version):
        self.app.SetLabel(u"%s %s" % (name, version))
    
    def SetAuthor(self, author):
        self.author.SetLabel(author)
    
    def SetWebsite(self, URL):
        #self.website.SetLabel(URL)
        #self.website.SetURL(URL)
        #self.website.Create(-1, URL, URL)
        return wx.HyperlinkCtrl(self, -1, URL, URL)
    
    def SetDescription(self, desc):
        self.description.SetLabel(desc)
    
    def AddDeveloper(self, name, email):
        next = self.credits.GetItemCount()
        self.credits.InsertStringItem(next, name)
        self.credits.SetStringItem(next, 2, email)
        self.credits.SetStringItem(next, 1, _(u'Developer'))
        #self.credits.SetItemTextColour(next, (255,255,255,255))
    
    def AddPackager(self, name, email):
        next = self.credits.GetItemCount()
        self.credits.InsertStringItem(next, name)
        self.credits.SetStringItem(next, 2, email)
        self.credits.SetStringItem(next, 1, _(u'Packager'))
        #self.credits.SetItemTextColour(next, (255,255,255,255))
    
    def AddJob(self, name, job, email):
        next = self.credits.GetItemCount()
        self.credits.InsertStringItem(next, name)
        self.credits.SetStringItem(next, 2, email)
        self.credits.SetStringItem(next, 1, job)
    
    def NoResizeCol(self, event):
        event.Veto()
    
    def SetChangelog(self, log):
        self.changelog.SetValue(log)
        self.changelog.SetInsertionPoint(0)
    
    def SetLicense(self, license):
        self.license.SetValue(license)
        self.license.SetInsertionPoint(0)
    
    def OnOk(self, event):
        self.Close()
    
