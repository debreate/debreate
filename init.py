#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

## Script to set configurations and launch Debreate
#  
#  Checks if the config file exists in ~/.config/debreate. If
#  not, a new file will be created (~/.config/debreate/config).
#  If the config file already exists but is corrupted, it will
#  reset it to its default settings.


# Modules to define required version of wx
import wxversion
wxversion.select([u'3.0', u'2.8'])

# System modules
import wx, os, sys, shutil

debreate_app = wx.App()


# Local modules
import main, dbr
from dbr import Logger


script_name = os.path.basename(__file__)

Logger.Info(script_name, u'Python version: {}'.format(dbr.PY_VER_STRING))
Logger.Info(script_name, u'wx.Python version: {}'.format(dbr.WX_VER_STRING))
Logger.Info(script_name, u'Debreate version: {}'.format(dbr.VERSION_STRING))

# Python & wx.Python encoding to UTF-8
if (sys.getdefaultencoding() != u'utf-8'):
    reload(sys)
    # FIXME: Recommended not to use
    sys.setdefaultencoding(u'utf-8')
wx.SetDefaultPyEncoding('UTF-8')

# wx.Widgets
# Get command line arguments
project_file = 0 # Set project file to false
if len(sys.argv) > 1:
    arg1 = sys.argv[1]
    filename = sys.argv[1] # Get the filename to show in window title
    if os.path.isfile(arg1):
        arg1 = open(arg1, u'r')
        project_file = arg1.read()
        arg1.close()

import dbr.command_line as CL

CL.ParseArguments(sys.argv[1:])
CL.ExecuteArguments()

# Set the path for the config file
dbdir = u'{}/.config/debreate'.format(dbr.home_path)
dbconfig = u'{}/config'.format(dbdir)

# Function to create the config file
def MakeConfig():
    # Make Debreate's config file
    config = open(dbconfig, u'w')
    config.write(u'[CONFIG-1.1]\n\
position=0,0\n\
size=800,650\n\
maximize=0\n\
center=1\n\
dialogs=0\n\
workingdir={}'.format(dbr.home_path))
    config.close()


def StartFirstRun():
    app = wx.App()
    frame = FirstRun(None, -1, _(u'Debreate First Run'))
#	frame.SetMessage(u'Thank you for using Debreate.\n\nThis message only displays the first time you run Debreate, \
#or if the configuration file becomes corrupted.')
    
    # Temporary message while in pre-alpha
#	frame.SetMessage(u'Creating the default configuration file.  To delete this file type \
#the following command in a terminal\n\n\
#rm -r ~/.debreate\n\n\
#!!--> Debreate 0.7 is still in pre-alpha.  This software is not fully functional. <--!!')
    
    # Temporary message while in alpha
    m1 = _(u'Thank you for using Debreate.')
    m2 = _(u'This message only displays on the first run, or if the configuration file becomes corrupted. The default configuration file will now be created. To delete this file, type the following command in a terminal:')
    frame.SetMessage(u'{}\n\n\
{}\n\n\
rm -r ~/.config/debreate'.format(m1, m2))
    
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
    frame = main.MainWindow(u'', pos, size)
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
        dbr.Mandatory = u'darkred'
        dbr.Recommended = u'darkblue'
    dbr.Optional = dummy.GetBackgroundColour()
    dbr.Disabled = frame.GetBackgroundColour()
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
    debreate_app.MainLoop()
    
    # Clean up the logger
    Logger.OnClose()


class FirstRun(wx.Dialog):
    '''Create the config file on first run or if file has been corrupted'''
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(450,300))
        
        # "OK" button sets to True
        self.OK = False
        
        # Set the titlebar icon
        self.SetIcon(wx.Icon(u'{}/bitmaps/debreate64.png'.format(dbr.application_path), wx.BITMAP_TYPE_PNG))
        
        # Display a message to create a config file
        self.message = wx.StaticText(self, -1)
        
        # Show the Debreate icon
        dbicon = wx.Bitmap(u'{}/bitmaps/debreate64.png'.format(dbr.application_path), wx.BITMAP_TYPE_PNG)
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
    old_config = u'{}/.debreate'.format(dbr.home_path)
    if os.path.isdir(old_config):
        Logger.Info(__name__, _(u'Found deprecated configuration, deleting...'))
        shutil.rmtree(old_config)
    
    # Check if config file exists
    if not os.path.isfile(dbconfig):
        Logger.Info(__name__, _(u'Config not found, launching "First Run"'))
        StartFirstRun()
        return True # Centers the window

    # Check if config file in right format
    else:
        # Read the config file
        file = open(dbconfig, u'r')
        conf = file.read()
        lines = conf.split(u'\n')
        file.close()

        # Split the lines into categories
        found = {}
        for line in lines:
            if u'=' in line:
                cat = line.split(u'=')
                found[cat[0]] = cat[1]

        # Check if categories are right type
        try:
            pos = tuple(int(n) for n in found[u'position'].split(u','))
            size = tuple(int(n) for n in found[u'size'].split(u','))
            maximize = int(found[u'maximize'])
            center = int(found[u'center'])
            dias = int(found[u'dialogs'])
            cwd = found[u'workingdir']
            if os.path.isdir(cwd) == False:
                firstrun = True
        except:
            Logger.Info(__name__, _(u'Error found in config file, running first start'))
            firstrun = True
        
        
        if firstrun:
            StartFirstRun()
            return True # Centers the window
        else:
            # If everything check out, start Debreate
            Run(pos, size, maximize, center, dias, cwd)


TestConfig()
