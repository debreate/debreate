# -*- coding: utf-8 -*-

## \package ui.about

# MIT licensing
# See: docs/LICENSE.txt


import commands, os, shutil, wx

from dbr.dialogs            import ShowErrorDialog
from dbr.font               import MONOSPACED_MD
from dbr.functions          import CreateTempDirectory
from dbr.functions          import GetContainerItemCount
from dbr.functions          import RemoveTempDirectory
from dbr.language           import GT
from dbr.listinput          import ListCtrlPanel
from dbr.log                import Logger
from dbr.textinput          import TextAreaPanel
from globals.application    import APP_name
from globals.application    import AUTHOR_email
from globals.application    import AUTHOR_name
from globals.constants      import INSTALLED
from globals.constants      import PREFIX
from globals.dateinfo       import GetYear
from globals.execute        import GetExecutable
from globals.fileio         import ReadFile
from globals.mime           import GetFileMimeType
from globals.paths          import PATH_app
from globals.system         import OS_codename
from globals.system         import OS_name
from globals.system         import OS_upstream_codename
from globals.system         import OS_upstream_name
from globals.system         import OS_upstream_version
from globals.system         import OS_version
from globals.system         import PY_VER_STRING
from globals.system         import WX_VER_STRING
from ui.button              import ButtonConfirm
from ui.hyperlink           import Hyperlink


# Font for the name
bigfont = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)
sys_info_font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)


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
    def __init__(self, parent, size=(600,558)):
        wx.Dialog.__init__(self, parent, wx.ID_ABOUT, GT(u'About'), size=size,
                           style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        
        self.SetMinSize(wx.Size(400, 375))
        self.CenterOnParent()
        
        # Create a tabbed interface
        tabs = wx.Notebook(self, -1)
        
        # Pages
        self.t_about = wx.Panel(tabs, -1)
        t_credits = wx.Panel(tabs, -1)
        t_changelog = wx.Panel(tabs, -1)
        t_license = wx.Panel(tabs, -1)
        
        # Add pages to tabbed interface
        tabs.AddPage(self.t_about, GT(u'About'))
        tabs.AddPage(t_credits, GT(u'Credits'))
        tabs.AddPage(t_changelog, GT(u'Changelog'))
        tabs.AddPage(t_license, GT(u'License'))
        
        # FIXME: Center verticall on about tab
        self.about_layout_V1 = wx.BoxSizer(wx.VERTICAL)
        self.about_layout_V1.AddStretchSpacer()
        self.about_layout_V1.AddStretchSpacer()
        
        self.t_about.SetAutoLayout(True)
        self.t_about.SetSizer(self.about_layout_V1)
        self.t_about.Layout()
        
        ## List of credits
        self.credits = ListCtrlPanel(t_credits)
        self.credits.SetSingleStyle(wx.LC_REPORT)
        self.credits.InsertColumn(0, GT(u'Name'), width=150)
        self.credits.InsertColumn(1, GT(u'Job'), width=200)
        self.credits.InsertColumn(2, GT(u'Email'), width=240)
        
        credits_sizer = wx.BoxSizer(wx.VERTICAL)
        credits_sizer.Add(self.credits, 1, wx.EXPAND)
        
        t_credits.SetAutoLayout(True)
        t_credits.SetSizer(credits_sizer)
        t_credits.Layout()
        
        ## Changelog text area
        self.changelog = TextAreaPanel(t_changelog, style=wx.TE_READONLY)
        self.changelog.SetFont(MONOSPACED_MD)
        
        log_sizer = wx.BoxSizer(wx.VERTICAL)
        log_sizer.Add(self.changelog, 1, wx.EXPAND)
        
        t_changelog.SetSizer(log_sizer)
        t_changelog.Layout()
        
        
        ## Licensing information text area
        self.license = TextAreaPanel(t_license, style=wx.TE_READONLY)
        self.license.SetFont(MONOSPACED_MD)
        
        license_sizer = wx.BoxSizer(wx.VERTICAL)
        license_sizer.Add(self.license, 1, wx.EXPAND)
        
        t_license.SetSizer(license_sizer)
        t_license.Layout()
        
        
        # System info
        sys_info = wx.Panel(tabs, -1)
        tabs.AddPage(sys_info, GT(u'System Information'))
        
        ## System's <a href="https://www.python.org/">Python</a> version
        self.py_info = wx.StaticText(sys_info, -1,
                GT(u'Python version: {}').format(PY_VER_STRING))
        
        ## System's <a href="https://wxpython.org/">wxPython</a> version
        self.wx_info = wx.StaticText(sys_info, -1,
                GT(u'wxPython version: {}').format(WX_VER_STRING))
        
        ## Debreate's installation prefix
        install_prefix = wx.StaticText(sys_info,
                label=GT(u'App location: {}').format(PATH_app))
        
        if INSTALLED:
            install_prefix.SetLabel(GT(u'Installation prefix: {}').format(PREFIX))
        
        self.py_info.SetFont(sys_info_font)
        self.wx_info.SetFont(sys_info_font)
        
        
        sysinfo_layout_V1 = wx.BoxSizer(wx.VERTICAL)
        sysinfo_layout_V1.AddStretchSpacer()
        sysinfo_layout_V1.Add(self.py_info, 0, wx.ALIGN_CENTER|wx.BOTTOM, 5)
        sysinfo_layout_V1.Add(self.wx_info, 0, wx.ALIGN_CENTER|wx.TOP, 5)
        sysinfo_layout_V1.AddSpacer(20)
        sysinfo_layout_V1.Add(install_prefix, 0, wx.ALIGN_CENTER|wx.TOP, 5)
        sysinfo_layout_V1.AddStretchSpacer()
        
        if OS_name:
            os_info = wx.StaticText(sys_info, label=OS_name)
            os_info.SetFont(sys_info_font)
            
            if OS_version:
                os_info.SetLabel(u'{} {}'.format(os_info.LabelText, OS_version))
            
            if OS_codename:
                os_info.SetLabel(u'{} {}'.format(os_info.LabelText, OS_codename))
            
            sysinfo_layout_V1.Insert(1, os_info, 0, wx.ALIGN_CENTER|wx.BOTTOM, 5)
            sysinfo_layout_V1.InsertSpacer(2, 20)
            
            if OS_upstream_name:
                os_upstream_info = wx.StaticText(sys_info, label=OS_upstream_name)
                
                if OS_upstream_version:
                    os_upstream_info.SetLabel(u'{} {}'.format(os_upstream_info.LabelText, OS_upstream_version))
                
                if OS_upstream_codename:
                    os_upstream_info.SetLabel(u'{} {}'.format(os_upstream_info.LabelText, OS_upstream_codename))
                
                sysinfo_layout_V1.Insert(2, os_upstream_info, 0, wx.ALIGN_CENTER|wx.BOTTOM, 5)
                
        
        sys_info.SetSizer(sysinfo_layout_V1)
        sys_info.Layout()
        
        
        # Button to close the dialog
        btn_confirm = ButtonConfirm(self)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tabs, 1, wx.EXPAND)
        sizer.Add(btn_confirm, 0, wx.ALIGN_RIGHT|wx.RIGHT|wx.TOP|wx.BOTTOM, 5)
        
        self.SetSizer(sizer)
        self.Layout()
    
    
    ## Displays logo in 'about' tab
    #  
    #  \param graphic
    #        Path to image file
    def SetGraphic(self, graphic):
        insertion_point = GetContainerItemCount(self.about_layout_V1) - 1
        
        image = wx.Image(graphic)
        image.Rescale(64, 64, wx.IMAGE_QUALITY_HIGH)
        
        self.about_layout_V1.Insert(
            insertion_point,
            wx.StaticBitmap(self.t_about, wx.ID_ANY, image.ConvertToBitmap()),
            0,
            wx.ALL|wx.ALIGN_CENTER,
            10
        )
        
        self.t_about.Layout()
    
    
    ## Displays version in 'about' tab
    #  
    #  \param version
    #        String to display
    def SetVersion(self, version):
        insertion_point = GetContainerItemCount(self.about_layout_V1) - 1
        
        app_label = wx.StaticText(
            self.t_about,
            label=u'{} {}'.format(APP_name, version)
        )
        app_label.SetFont(bigfont)
        
        self.about_layout_V1.Insert(
            insertion_point,
            app_label,
            0,
            wx.ALL|wx.ALIGN_CENTER,
            10
        )
        
        self.t_about.Layout()
    
    
    ## Display author's name
    #  
    #  \param author
    #        String to display
    def SetAuthor(self, author):
        insertion_point = GetContainerItemCount(self.about_layout_V1) - 1
        
        self.about_layout_V1.Insert(
            insertion_point,
            wx.StaticText(self.t_about, label=author),
            0,
            wx.ALL|wx.ALIGN_CENTER,
            10
        )
        
        self.t_about.Layout()
    
    
    ## Sets a hotlink to the app's homepage
    #  
    #  TODO: Remove: Deprecated, unused
    #  \param URL
    #        URL to open when link is clicked
    def SetWebsite(self, URL):
        self.website.SetLabel(URL)
        self.website.SetURL(URL)
    
    
    ## Adds URL hotlinks to about dialog
    #  
    #  \param url_list
    #        \b \e tuple : Website labels & URL definitions
    def SetWebsites(self, url_list):
        insertion_point = GetContainerItemCount(self.about_layout_V1) - 1
        
        link_layout = wx.BoxSizer(wx.VERTICAL)
        for label, link in url_list:
            link_layout.Add(
                Hyperlink(self.t_about, wx.ID_ANY, label=label, url=link),
                0,
                wx.ALIGN_CENTER,
                10
            )
        
        self.about_layout_V1.Insert(
            insertion_point,
            link_layout,
            0,
            wx.ALL|wx.ALIGN_CENTER,
            10
        )
        self.t_about.Layout()
    
    
    ## Displays a description about the app on the 'about' tab
    def SetDescription(self, desc):
        # Place between spacers
        insertion_point = GetContainerItemCount(self.about_layout_V1) - 1
        
        self.about_layout_V1.Insert(
            insertion_point,
            wx.StaticText(self.t_about, label=desc),
            0,
            wx.ALL|wx.ALIGN_CENTER,
            10
        )
        
        self.t_about.Layout()
    
    
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
        self.credits.SetStringItem(next_item, 1, GT(u'Developer'))
    
    
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
        self.credits.SetStringItem(next_item, 1, GT(u'Packager'))
    
    
    ## Adds a translator to the list of credits
    #  
    #  \param name
    #        \b \e str : Translator's name
    #  \param email
    #        \b \e str : Translator's email address
    #  \param lang
    #        \b \e str : Locale code for the translation
    def AddTranslator(self, name, email, lang):
        job = GT(u'Translation')
        job = u'{} ({})'.format(job, lang)
        next_item = self.credits.GetItemCount()
        self.credits.InsertStringItem(next_item, name)
        self.credits.SetStringItem(next_item, 2, email)
        self.credits.SetStringItem(next_item, 1, job)
    
    
    ## Adds a general job to the credits list
    #  
    #  \param name
    #        \b \e str : Contributer's name
    #  \param job
    #        \b \e str : Job description
    #  \param email
    #        \b \e str : Job holder's email address
    def AddJob(self, name, job, email=wx.EmptyString):
        next_item = self.credits.GetItemCount()
        self.credits.InsertStringItem(next_item, name)
        self.credits.SetStringItem(next_item, 1, job)
        
        if email != wx.EmptyString:
            self.credits.SetStringItem(next_item, 2, email)
    
    
    ## Adds list of jobs for single contributer
    #
    #  \param name
    #        \b \e unicode|str : Contributer's name
    #  \param jobs
    #        \b \e string \b \e list|tuple : Contributer's jobs
    #  \param email
    #        \b \e unicode|str : Optional contributer's email address
    def AddJobs(self, name, jobs, email=wx.EmptyString):
        if isinstance(jobs, str) or isinstance(jobs, unicode):
            Logger.Debug(__name__, GT(u'Converting string argument "jobs" to tuple'))
            jobs = (jobs,)
        
        for x, value in enumerate(jobs):
            next_item = self.credits.GetItemCount()
            if x == 0:
                self.credits.InsertStringItem(next_item, name)
                if email != wx.EmptyString:
                    self.credits.SetStringItem(next_item, 2, email)
            else:
                self.credits.InsertStringItem(next_item, wx.EmptyString)
            
            self.credits.SetStringItem(next_item, 1, value)
    
    # FIXME: Unused?
    def NoResizeCol(self, event=None):
        if event:
            event.Veto()
    
    
    ## Sets text to be shown on the 'Changelog' tab
    #  
    #  FIXME: Change to create in class constructor
    #  \param log_file
    #        \b \e str : Path to changelog file on filesystem
    def SetChangelog(self):
        ## Defines where the changelog is located
        #  
        #  By default it is located in the folder 'doc'
        #   under the applications root directory. The
        #   install script or Makefile should change this
        #   to reflect installed path.
        if INSTALLED:
            # FIXME: Read compressed .gz changelog
            CHANGELOG = u'{}/share/doc/debreate/changelog.gz'.format(PREFIX)
        
        else:
            CHANGELOG = u'{}/docs/changelog'.format(PREFIX)
        
        if os.path.isfile(CHANGELOG):
            changelog_mimetype = GetFileMimeType(CHANGELOG)
            
            Logger.Debug(__name__, GT(u'Changelog mimetype: {}').format(changelog_mimetype))
            
            # Set log text in case of read error
            log_text = GT(u'Error reading changelog: {}\n\t').format(CHANGELOG)
            log_text = u'{}{}'.format(log_text,
                                      GT(u'Cannot decode, unrecognized mimetype: {}').format(changelog_mimetype))
            
            if changelog_mimetype == u'application/gzip':
                temp_dir = CreateTempDirectory()
                
                shutil.copy(CHANGELOG, temp_dir)
                
                CMD_gzip = GetExecutable(u'gzip')
                
                if CMD_gzip:
                    prev_dir = os.getcwd()
                    os.chdir(temp_dir)
                    
                    gzip_output = commands.getstatusoutput(u'{} -fd {}'.format(CMD_gzip, os.path.basename(CHANGELOG)))
                    
                    Logger.Debug(__name__,
                            GT(u'gzip decompress; Code: {}, Output: {}').format(gzip_output[0], gzip_output[1]))
                    
                    os.chdir(prev_dir)
                
                changelog_file = os.path.basename(CHANGELOG).split(u'.')[0]
                changelog_file = u'{}/{}'.format(temp_dir, changelog_file)
                
                if os.path.isfile(changelog_file):
                    log_text = ReadFile(changelog_file)
                
                RemoveTempDirectory(temp_dir)
            
            elif changelog_mimetype == u'text/plain':
                log_text = ReadFile(CHANGELOG)
            
            else:
                ShowErrorDialog(log_text, parent=self)
        
        else:
            log_text = GT(u'ERROR: Could not locate changelog file:\n\t\'{}\' not found'.format(CHANGELOG))
        
        self.changelog.SetValue(log_text)
        self.changelog.SetInsertionPoint(0)
    
    
    ## Sets text to be shown on the 'License' tab
    #  
    #  \param lic_file
    #        \b \e : Path to license file on the filesystem
    def SetLicense(self):
        ## Defines where the LICENSE.txt is located
        #  
        #  By default it is located in the folder 'doc'
        #   under the applications root directory. The
        #   install script or Makefile should change this
        #   to reflect installed path.
        if INSTALLED:
            license_path = u'{}/share/doc/debreate/copyright'.format(PREFIX)
        
        else:
            license_path = u'{}/docs/LICENSE.txt'.format(PREFIX)
        
        if os.path.isfile(license_path):
            lic_text = ReadFile(license_path)
        
        else:
            lic_text = GT(u'ERROR: Could not locate license file:\n\t\'{}\' not found'.format(license_path))
            lic_text += u'\n\nCopyright © {} {} <{}>'.format(GetYear(), AUTHOR_name, AUTHOR_email)
            lic_text += u'\n\nhttps://opensource.org/licenses/MIT'
        
        self.license.SetValue(lic_text)
        self.license.SetInsertionPoint(0)
    
    
    ## Defines action to take when 'Ok' button is press
    #  
    #  Closes the dialog.
    #  \param event
    #        <b><em>(wx.EVT_BUTTON)</em></b>
    def OnOk(self, event=None):
        self.Close()
