# -*- coding: utf-8 -*-

## \package dbr.about
#  Dialog that shows information about the application


import wx

import dbr


## Dialog that shows information about the application
class AboutDialog(wx.Dialog):
    ## Constructor
    #  
    #  \param parent
    #        The parent window
    #  \param id
    #        Window id (FIXME: Not necessary)
    #  \param title
    #        Text to be shown in the title bar
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(400,375))
        
        # Font for the name
        bigfont = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        sys_info_font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        
        # Create a tabbed interface
        tabs = wx.Notebook(self, -1)
        #tabs.SetForegroundColour((255,255,255,255))
        #tabs.SetBackgroundColour((50,50,50,50))
        
        # Pages
        about = wx.Panel(tabs, -1)
        #about.SetBackgroundColour((0,0,0,0))
        credits = wx.Panel(tabs, -1)
        changelog = wx.Panel(tabs, -1)
        license = wx.Panel(tabs, -1)
        
        # Add pages to tabbed interface
        tabs.AddPage(about, _(u'About'))
        tabs.AddPage(credits, _(u'Credits'))
        tabs.AddPage(changelog, _(u'Changelog'))
        tabs.AddPage(license, _(u'License'))
        
        ## Application logo
        self.graphic = wx.StaticBitmap(about)
        
        ## Name & version of the application
        self.app = wx.StaticText(about, -1)
        self.app.SetFont(bigfont)
        
        ## Application author
        self.author = wx.StaticText(about)
        
        ## Application's homepage
        self.website = wx.HyperlinkCtrl(about, -1,
                'debreate.sourceforge.net', 'http://debreate.sourceforge.net/')
        
        ## Application's secondary homepage
        self.website2 = wx.HyperlinkCtrl(about, -1,
                'github.com/AntumDeluge/debreate', 'https://github.com/AntumDeluge/debreate')
        
        ## Short description
        self.description = wx.StaticText(about, -1)
        
        link_sizer = wx.BoxSizer(wx.VERTICAL)
        link_sizer.Add(self.website, 0, wx.ALIGN_CENTER, 10)
        link_sizer.Add(self.website2, 0, wx.ALIGN_CENTER, 10)
        
        about_sizer = wx.BoxSizer(wx.VERTICAL)
        about_sizer.AddMany( [
            (self.graphic, 0, wx.ALIGN_CENTER|wx.ALL, 10),
            (self.app, 0, wx.ALIGN_CENTER|wx.ALL, 10),
            (self.author, 0, wx.ALIGN_CENTER|wx.ALL, 10),
            (link_sizer, 0, wx.ALIGN_CENTER|wx.ALL, 10),
            (self.description, 0, wx.ALIGN_CENTER|wx.ALL, 10)
            ] )
        
        about.SetAutoLayout(True)
        about.SetSizer(about_sizer)
        about.Layout()
        
        ## List of credits
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
        
        ## Changelog text area
        self.changelog = wx.TextCtrl(changelog, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        #self.changelog.SetBackgroundColour((0,0,0,0))
        #self.changelog.SetForegroundColour((255,255,255,255))
        
        log_sizer = wx.BoxSizer(wx.VERTICAL)
        log_sizer.Add(self.changelog, 1, wx.EXPAND)
        
        changelog.SetSizer(log_sizer)
        changelog.Layout()
        
        
        ## Licensing information text area
        self.license = wx.TextCtrl(license, -1, style=wx.TE_READONLY|wx.TE_MULTILINE)
        #self.license.SetBackgroundColour((0,0,0,0))
        #self.license.SetForegroundColour((255,255,255,255))
        
        license_sizer = wx.BoxSizer(wx.VERTICAL)
        license_sizer.Add(self.license, 1, wx.EXPAND)
        
        license.SetSizer(license_sizer)
        license.Layout()
        
        
        # System info
        sys_info = wx.Panel(tabs, -1)
        tabs.AddPage(sys_info, _(u'System Information'))
        
        ## System's <a href="https://www.python.org/">Python</a> version
        self.py_info = wx.StaticText(sys_info, -1,
                _(u'Python version: {}').format(dbr.PY_VER_STRING))
        
        ## System's <a href="https://wxpython.org/">wxPython</a> version
        self.wx_info = wx.StaticText(sys_info, -1,
                _(u'wxPython version: {}').format(dbr.WX_VER_STRING))
        
        self.py_info.SetFont(sys_info_font)
        self.wx_info.SetFont(sys_info_font)
        
        
        sys_info_sizer = wx.BoxSizer(wx.VERTICAL)
        sys_info_sizer.AddSpacer(20, wx.EXPAND|wx.ALL)  # FIXME: Want to center elements on panel
        sys_info_sizer.Add(self.py_info, 0, wx.ALIGN_CENTER|wx.BOTTOM, 5)
        sys_info_sizer.Add(self.wx_info, 0, wx.ALIGN_CENTER|wx.TOP, 5)
        
        sys_info.SetSizer(sys_info_sizer)
        sys_info.Layout()
        
        
        # Button to close the dialog
        ok = dbr.ButtonConfirm(self)#wx.Button(self, wx.OK, "Ok")
        #wx.EVT_BUTTON(ok, wx.OK, self.OnOk)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tabs, 1, wx.EXPAND)
        sizer.Add(ok, 0, wx.ALIGN_RIGHT|wx.RIGHT|wx.TOP, 5)
        
        self.SetSizer(sizer)
        self.Layout()
    
    
    ## Displays logo in 'about' tab
    #  
    #  \param graphic
    #        Path to image file
    def SetGraphic(self, graphic):
        image = wx.Image(graphic)
        image.Rescale(64, 64, wx.IMAGE_QUALITY_HIGH)
        self.graphic.SetBitmap(image.ConvertToBitmap())
    
    ## Displays version in 'about' tab
    #  
    #  \param version
    #        String to display
    def SetVersion(self, version):
        self.app.SetLabel(u"%s %s" % (dbr.APP_NAME, version))
    
    ## Display author's name
    #  
    #  \param author
    #        String to display
    def SetAuthor(self, author):
        self.author.SetLabel(author)
    
    ## Sets a hotlink to the app's homepage
    #  
    #  \param URL
    #        URL to open when link is clicked
    def SetWebsite(self, URL):
        self.website.SetLabel(URL)
        self.website.SetURL(URL)
    
    ## Displays a description about the app on the 'about' tab
    def SetDescription(self, desc):
        self.description.SetLabel(desc)
    
    ## Adds a developer to the list of credits
    #  
    #  \param name
    #        str: Developer's name
    #  \param email
    #        str: Developer's email address
    def AddDeveloper(self, name, email):
        next_item = self.credits.GetItemCount()
        self.credits.InsertStringItem(next_item, name)
        self.credits.SetStringItem(next_item, 2, email)
        self.credits.SetStringItem(next_item, 1, _(u'Developer'))
        #self.credits.SetItemTextColour(next_item, (255,255,255,255))
    
    ## Adds a packager to the list of credits
    #  
    #  \param name
    #        \b \e str : Packager's name
    #  \param email
    #        \b \e str : Packager's email address
    def AddPackager(self, name, email):
        next_item = self.credits.GetItemCount()
        self.credits.InsertStringItem(next_item, name)
        self.credits.SetStringItem(next_item, 2, email)
        self.credits.SetStringItem(next_item, 1, _(u'Packager'))
        #self.credits.SetItemTextColour(next_item, (255,255,255,255))
    
    ## Adds a translator to the list of credits
    #  
    #  \param name
    #        \b \e str : Translator's name
    #  \param email
    #        \b \e str : Translator's email address
    #  \param lang
    #        \b \e str : Locale code for the translation
    def AddTranslator(self, name, email, lang):
        job = _(u'Translation')
        job = '{} ({})'.format(job, lang)
        next_item = self.credits.GetItemCount()
        self.credits.InsertStringItem(next_item, name)
        self.credits.SetStringItem(next_item, 2, email)
        self.credits.SetStringItem(next_item, 1, job)
    
    ## Adds a general job to the credits list
    #  
    #  \param name
    #        \b \e str : Name of job holder
    #  \param job
    #        \b \e str : Job description
    #  \param email
    #        \b \e str : Job holder's email address
    def AddJob(self, name, job, email):
        next_item = self.credits.GetItemCount()
        self.credits.InsertStringItem(next_item, name)
        self.credits.SetStringItem(next_item, 2, email)
        self.credits.SetStringItem(next_item, 1, job)
    
    def NoResizeCol(self, event):
        event.Veto()
    
    ## Sets text to be shown on the 'Changelog' tab
    #  
    #  \param log_file
    #        \b \e str : Path to changelog file on filesystem
    def SetChangelog(self, log_file):
        log_data = open(log_file)
        log_text = log_data.read()
        log_data.close()
        self.changelog.SetValue(log_text)
        self.changelog.SetInsertionPoint(0)
    
    ## Sets text to be shown on the 'License' tab
    #  
    #  \param lic_file
    #        \b \e : Path to license file on the filesystem
    def SetLicense(self, lic_file):
        lic_data = open(lic_file)
        lic_text = lic_data.read()
        lic_data.close()
        self.license.SetValue(lic_text)
        self.license.SetInsertionPoint(0)
    
    ## Defines action to take when 'Ok' button is press
    #  
    #  Closes the dialog.
    #  \param event
    #        <b><em>(wx.EVT_BUTTON)</em></b>
    def OnOk(self, event):
        self.Close()
    
