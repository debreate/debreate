#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Script to set configurations and launch Debreate
# First this script will see if the config file exists in ~/.debreate.  If not a file will be created
# (~/.config/debreate/config).  If the config file already exists and is corrupted, this script will bring it
# back to its default settings.

from common import setWXVersion
setWXVersion()

import wx, sys, os, debreate, db, language, shutil

# Get command line arguments
project_file = 0 # Set project file to false
if len(sys.argv) > 1:
    arg1 = sys.argv[1]
    filename = sys.argv[1] # Get the filename to show in window title
    if os.path.isfile(arg1):
        arg1 = open(arg1, "r")
        project_file = arg1.read()
        arg1.close()


# Get path to folder where script resides
application_path = debreate.application_path

# Get the user's home directory
home = os.getenv('HOME')

# Set the path for the config file
dbdir = "%s/.config/debreate" % (home)
dbconfig = "%s/config" % (dbdir)

# Function to create the config file
def MakeConfig():
    # Make Debreate's config file
    config = open(dbconfig, 'w')
    config.write("[CONFIG-1.1]\n\
position=0,0\n\
size=800,650\n\
maximize=0\n\
center=1\n\
dialogs=0\n\
workingdir=%s" % home)
    config.close()


def StartFirstRun():
    app = wx.App()
    frame = FirstRun(None, -1, _('Debreate First Run'))
#	frame.SetMessage("Thank you for using Debreate.\n\nThis message only displays the first time you run Debreate, \
#or if the configuration file becomes corrupted.")
    
    # Temporary message while in pre-alpha
#	frame.SetMessage("Creating the default configuration file.  To delete this file type \
#the following command in a terminal\n\n\
#rm -r ~/.debreate\n\n\
#!!--> Debreate 0.7 is still in pre-alpha.  This software is not fully functional. <--!!")
    
    # Temporary message while in alpha
    m1 = _('Thank you for using Debreate.')
    m2 = _('This message only displays on the first run, or if the configuration file becomes corrupted. The default configuration file will now be created. To delete this file, type the following command in a terminal:')
    frame.SetMessage('%s\n\n\
%s\n\n\
rm -r ~/.config/debreate' % (m1, m2))
    
    frame.ShowModal()
    if frame.OK:
        frame.Destroy()
        app.MainLoop()
        TestConfig()
    else:
        frame.Destroy()
        app.MainLoop()


def Run(pos, size, maximize, center, dias, cwd):
    # Start the main application window
    app = wx.App()
    frame = debreate.MainWindow(None, -1, "", pos, size)
    frame.SetTitle(frame.default_title)
    
    # Find out if user is using a dark theme (font will be light)
    # Then we can change the priority colors according to that theme
    darktheme = False
    # Create a dummy text control to get theme colors
    dummy = wx.TextCtrl(frame)
    fg_color = dummy.GetForegroundColour()
    for rgb in fg_color:
        if rgb > 150:
            darktheme = True
    if darktheme:
        # This sets the colors for text controls with priorities by using a text control
        # from the control page before priority colors are applied
        db.Mandatory = "darkred"
        db.Recommended = "darkblue"
    db.Optional = dummy.GetBackgroundColour()
    db.Disabled = frame.GetBackgroundColour()
    # Get rid of the dummy text control
    dummy.Destroy()
    
    if project_file:
        frame.OpenProject(project_file, filename)
    else:
        # Change current working directory
        os.chdir(cwd)
    
    if center:
        # Center the window
        frame.Center()
    if maximize:
        # Maximize the window
        frame.Maximize()
    
    if dias:
        # Uses custom dialogs
        frame.cust_dias.Check()
    
    # Send the configuration path to Debreate
    frame.dbdir = dbdir
    frame.dbconfig = dbconfig
    
    frame.Show()
    app.MainLoop()


class FirstRun(wx.Dialog):
    """Create the config file on first run or if file has been corrupted"""
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(450,300))
        
        # "OK" button sets to True
        self.OK = False
        
        # Set the titlebar icon
        self.SetIcon(wx.Icon("%s/bitmaps/debreate64.png" % application_path, wx.BITMAP_TYPE_PNG))
        
        # Display a message to create a config file
        self.message = wx.StaticText(self, -1)
        
        # Show the Debreate icon
        dbicon = wx.Bitmap("%s/bitmaps/debreate64.png" % application_path, wx.BITMAP_TYPE_PNG)
        icon = wx.StaticBitmap(self, -1, dbicon)
        
        # Button to confirm
        self.button_ok = wx.Button(self, wx.ID_OK)
        
        wx.EVT_BUTTON(self.button_ok, -1, self.OnOk)
        
        # Nice border
        self.border = wx.StaticBox(self, -1)
        border_box = wx.StaticBoxSizer(self.border, wx.HORIZONTAL)
        border_box.AddSpacer(10)
        border_box.Add(icon, 0, wx.ALIGN_CENTER)
        border_box.AddSpacer(10)
        border_box.Add(self.message, 1, wx.ALIGN_CENTER)
        
        # Set Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(border_box, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        sizer.Add(self.button_ok, 0, wx.ALIGN_RIGHT|wx.RIGHT|wx.BOTTOM|wx.TOP, 5)
        
        self.SetSizer(sizer)
        self.Layout()
    
    def SetMessage(self, message):
        self.message.SetLabel(message)
        #self.message.Wrap(00)
    
    def OnOk(self, event):
        # See if the config file exists
        if not os.path.isdir(dbdir):
            os.mkdir(dbdir)
        # Run function to create the config file
        MakeConfig()
        self.Close()
        self.OK = True


def TestConfig():
    # need to run first start program
    firstrun = False
    
    # Check for old config file
    old_config = '%s/.debreate' % home
    if os.path.isdir(old_config):
        print('Found deprecated configuration, deleting...')
        shutil.rmtree(old_config)
    
    # Check if config file exists
    if not os.path.isfile(dbconfig):
        print(_("Config not found, launching \"First Run\""))
        StartFirstRun()
        return True # Centers the window

    # Check if config file in right format
    else:
        # Read the config file
        file = open(dbconfig, 'r')
        conf = file.read()
        lines = conf.split('\n')
        file.close()

        # Split the lines into categories
        found = {}
        for line in lines:
            if '=' in line:
                cat = line.split('=')
                found[cat[0]] = cat[1]

        # Check if categories are right type
        try:
            pos = tuple(int(n) for n in found['position'].split(','))
            size = tuple(int(n) for n in found['size'].split(','))
            maximize = int(found['maximize'])
            center = int(found['center'])
            dias = int(found['dialogs'])
            cwd = found['workingdir']
            if os.path.isdir(cwd) == False:
                firstrun = True
        except:
            print(_("Error found in config file, running first start"))
            firstrun = True
        
        
        if firstrun:
            StartFirstRun()
            return True # Centers the window
        else:
            # If everything check out, start Debreate
            Run(pos, size, maximize, center, dias, cwd)


TestConfig()