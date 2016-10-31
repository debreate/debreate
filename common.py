# -*- coding: utf-8 -*-


import sys, os, subprocess, wx
from urllib2        import URLError
from urllib2        import urlopen
from wx.lib.docview import PathOnly


# Get path to folder where script resides
application_path = os.path.dirname(__file__)


RELEASE = 0
ver_maj = 0
ver_min = 7
ver_rel = 12

debreate_version = u'{}.{}.{}'.format(ver_maj, ver_min, ver_rel)

if not RELEASE:
    # Increment this for every development release
    ver_dev = 3
    debreate_version = u'{}-dev{}'.format(debreate_version, ver_dev)

db_version = (ver_maj, ver_min, ver_rel)
db_here = PathOnly(__file__).decode(u'utf-8')
db_website = u'http://debreate.sourceforge.net/'

maj_pyversion = sys.version_info[0]
mid_pyversion = sys.version_info[1]
min_pyversion = sys.version_info[2]
python_version = u'{}.{}.{}'.format(maj_pyversion, mid_pyversion, min_pyversion)

print("Python version: {}".format(python_version))
print("wxPython version: {}.{}.{}".format(wx.MAJOR_VERSION, wx.MINOR_VERSION, wx.RELEASE_VERSION))
print("Debreate version: {}.{}.{}".format(ver_maj, ver_min, ver_rel))



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


ID_APPEND = wx.NewId()
ID_OVERWRITE = wx.NewId()


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
            raise StandardError(_(u'Too many files'))
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
