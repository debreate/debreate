# -*- coding: utf-8 -*-

import sys, os
from urllib2 import urlopen, URLError, HTTPError
from wx.lib.docview import PathOnly


import wxversion
wxversion.select(['2.6', '2.7', '2.8'])
import wx

import language


# Set the encoding to unicode
if (sys.getdefaultencoding() != 'utf-8'):
    reload(sys)
    sys.setdefaultencoding('utf-8')
wx.SetDefaultPyEncoding('UTF-8')


dbr_release=True
maj_version = 0
mid_version = 7
min_version = 10

# For testing release
if (not dbr_release):
    min_version -= 0.5

debreate_version = u'%s.%s.%s' % (maj_version, mid_version, min_version)
db_version = (maj_version, mid_version, min_version)
db_here = PathOnly(__file__).decode(u'utf-8')
db_website = u'http://debreate.sourceforge.net'

maj_pyversion = sys.version_info[0]
mid_pyversion = sys.version_info[1]
min_pyversion = sys.version_info[2]
python_version = u'%s.%s.%s' % (maj_pyversion, mid_pyversion, min_pyversion)

print("Python version: %s" % python_version)
print("wxPython version: %s.%s.%s" % (wx.MAJOR_VERSION, wx.MINOR_VERSION, wx.RELEASE_VERSION))
print("Debreate version: %s.%s.%s" % (maj_version, mid_version, min_version))



##################
###     FUNCTIONS       ###
##################

def RequirePython(version):
    error = 'Incompatible python version'
    t = type(version)
    if t == type(''):
        if version == python_version[0:3]:
            return
        raise ValueError(error)
    elif t == type([]) or t == type(()):
        if python_version[0:3] in version:
            return
        raise ValueError(error)
    raise ValueError('Wrong type for argument 1 of RequirePython(version)')


def GetCurrentVersion():
    try:
        request = urlopen(u'%s/current.txt' % (db_website))
        version = request.readlines()[0]
        version = version.split('.')
        
        if ('\n' in version[-1]):
            # Remove newline character
            version[-1] = version[-1][:-1]
        
        # Convert to integer
        for v in range(0, len(version)):
            version[v] = int(version[v])
        
        # Change container to tuple and return it
        version = (version[0], version[1], version[2])
        return version
    
    except URLError, err:
        #err = unicode(err)
        return err


### -*- Execute commands with sudo privileges -*- ###
def RunSudo(password, command):
    command = u'echo %s | sudo -S %s ; echo $?' % (password, command)
    wx.SafeYield()
    output = os.popen(command).read()
    err = int(output.split(u'\n')[-2])
    if (err):
        return False
    return True


### -*- Function to check for installed executables -*- ###
def CommandExists(command):
    try:
        subprocess.Popen(command.split(u' ')[0].split(u' '))
        exists = True
        print u'First subprocess: %s' % (exists)
    except OSError:
        exists = os.path.isfile(command)
        print u'os.path: %s' % (exists)
        if exists:
            subprocess.Popen((command))
            print u'Second subprocess: %s' % (exists)
    return exists



################
###     CLASSES       ###
################

### -*- A very handy widget that captures stdout and stderr to a wx.TextCtrl -*- ###
class OutputLog(wx.TextCtrl):
    def __init__(self, parent, id=-1):
        wx.TextCtrl.__init__(self, parent, id, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.SetBackgroundColour(u'black')
        self.SetForegroundColour(u'white')
        self.stdout = sys.stdout
        self.stderr = sys.stderr
    
    def write(self, string):
        self.AppendText(string)
    
    def ToggleOutput(self, event=None):
        if (sys.stdout == self):
            sys.stdout = self.stdout
            sys.stderr = self.stderr
        else:
            sys.stdout = self
            sys.stdout = self


### -*- Dialog for overwrite prompt of a text area -*- ###
class OverwriteDialog(wx.Dialog):
    def __init__(self, parent, id=-1, title=_(u'Overwrite?'), message=u''):
        wx.Dialog.__init__(self, parent, id, title)
        self.message = wx.StaticText(self, -1, message)
        
        self.button_overwrite = wx.Button(self, ID_OVERWRITE, _(u'Overwrite'))
        self.button_append = wx.Button(self, ID_APPEND, _(u'Append'))
        self.button_cancel = wx.Button(self, wx.ID_CANCEL)
        
        ### -*- Button events -*- ###
        wx.EVT_BUTTON(self.button_overwrite, ID_OVERWRITE, self.OnButton)
        wx.EVT_BUTTON(self.button_append, ID_APPEND, self.OnButton)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.button_overwrite, 0, wx.LEFT|wx.RIGHT, 5)
        hsizer.Add(self.button_append, 0, wx.LEFT|wx.RIGHT, 5)
        hsizer.Add(self.button_cancel, 0, wx.LEFT|wx.RIGHT, 5)
        
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(self.message, 1, wx.ALIGN_CENTER|wx.ALL, 5)
        vsizer.Add(hsizer, 0, wx.ALIGN_RIGHT|wx.TOP|wx.BOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizerAndFit(vsizer)
        self.Layout()
    
    def OnButton(self, event):
        id = event.GetEventObject().GetId()
        self.EndModal(id)
    
    def GetMessage(self, event=None):
        return self.message.GetLabel()


### -*- Object for Dropping Text Files -*-
class SingleFileTextDropTarget(wx.FileDropTarget):
    def __init__(self, obj):
        wx.FileDropTarget.__init__(self)
        self.obj = obj
    
    def OnDropFiles(self, x, y, filenames):
        if len(filenames) > 1:
            raise BaseError(_(u'Too many files'))
        text = open(filenames[0]).read()
        try:
            if (not TextIsEmpty(self.obj.GetValue())):
                overwrite = OverwriteDialog(self.obj, message = _(u'The text area is not empty!'))
                id = overwrite.ShowModal()
                if (id == ID_OVERWRITE):
                    self.obj.SetValue(text)
                elif (id == ID_APPEND):
                    self.obj.SetInsertionPoint(-1)
                    self.obj.WriteText(text)
            else:
                self.obj.SetValue(text)
        except UnicodeDecodeError:
            wx.MessageDialog(None, _(u'Error decoding file'), _(u'Error'), wx.OK).ShowModal()


### -*- Checks if Text Control is Empty -*- ###
def TextIsEmpty(text):
    text = u''.join(u''.join(text.split(u' ')).split(u'\n'))
    return (text == u'')
