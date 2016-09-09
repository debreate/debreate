# -*- coding: utf-8 -*-


# wx system
from wximports import \
	wxMAJOR_VERSION, \
	wxMINOR_VERSION, \
	wxRELEASE_VERSION, \
	wxSetDefaultPyEncoding

# General wx imports
from wximports import \
	wxDialog, \
	wxFileDropTarget, \
	wxTextCtrl

# Text editing constants
from wximports import \
	wxTE_MULTILINE, \
	wxTE_READONLY

import sys, os
from wx.lib.docview import PathOnly


import language


# Set the encoding to unicode
if (sys.getdefaultencoding() != 'utf-8'):
    reload(sys)
    sys.setdefaultencoding('utf-8')
wxSetDefaultPyEncoding('UTF-8')


from dbr.constants import VERSION_STRING




db_here = PathOnly(__file__).decode(u'utf-8')

maj_pyversion = sys.version_info[0]
mid_pyversion = sys.version_info[1]
min_pyversion = sys.version_info[2]
python_version = u'{}.{}.{}'.format(maj_pyversion, mid_pyversion, min_pyversion)

print("Python version: {}".format(python_version))
print("wxPython version: {}.{}.{}".format(wxMAJOR_VERSION, wxMINOR_VERSION, wxRELEASE_VERSION))
print("Debreate version: {}".format(VERSION_STRING))



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



### -*- Execute commands with sudo privileges -*- ###
def RunSudo(password, command):
    command = u'echo %s | sudo -S %s ; echo $?' % (password, command)
    wxSafeYield()
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

### -*- A very handy widget that captures stdout and stderr to a wxTextCtrl -*- ###
class OutputLog(wxTextCtrl):
    def __init__(self, parent, id=-1):
        wxTextCtrl.__init__(self, parent, id, style=wxTE_MULTILINE|wxTE_READONLY)
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
class OverwriteDialog(wxDialog):
    def __init__(self, parent, id=-1, title=_(u'Overwrite?'), message=u''):
        wxDialog.__init__(self, parent, id, title)
        self.message = wxStaticText(self, -1, message)
        
        self.button_overwrite = wxButton(self, ID_OVERWRITE, _(u'Overwrite'))
        self.button_append = wxButton(self, ID_APPEND, _(u'Append'))
        self.button_cancel = wxButton(self, wxID_CANCEL)
        
        ### -*- Button events -*- ###
        wxEVT_BUTTON(self.button_overwrite, ID_OVERWRITE, self.OnButton)
        wxEVT_BUTTON(self.button_append, ID_APPEND, self.OnButton)
        
        hsizer = wxBoxSizer(wxHORIZONTAL)
        hsizer.Add(self.button_overwrite, 0, wxLEFT|wxRIGHT, 5)
        hsizer.Add(self.button_append, 0, wxLEFT|wxRIGHT, 5)
        hsizer.Add(self.button_cancel, 0, wxLEFT|wxRIGHT, 5)
        
        vsizer = wxBoxSizer(wxVERTICAL)
        vsizer.Add(self.message, 1, wxALIGN_CENTER|wxALL, 5)
        vsizer.Add(hsizer, 0, wxALIGN_RIGHT|wxTOP|wxBOTTOM, 5)
        
        self.SetAutoLayout(True)
        self.SetSizerAndFit(vsizer)
        self.Layout()
    
    def OnButton(self, event):
        id = event.GetEventObject().GetId()
        self.EndModal(id)
    
    def GetMessage(self, event=None):
        return self.message.GetLabel()


### -*- Object for Dropping Text Files -*-
class SingleFileTextDropTarget(wxFileDropTarget):
    def __init__(self, obj):
        wxFileDropTarget.__init__(self)
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
            wxMessageDialog(None, _(u'Error decoding file'), _(u'Error'), wxOK).ShowModal()


### -*- Checks if Text Control is Empty -*- ###
def TextIsEmpty(text):
    text = u''.join(u''.join(text.split(u' ')).split(u'\n'))
    return (text == u'')
