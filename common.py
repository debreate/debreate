# -*- coding: utf-8 -*-


import sys, os, subprocess
from wx import \
    BoxSizer as wxBoxSizer, \
    Button as wxButton, \
	Dialog as wxDialog, \
	FileDropTarget as wxFileDropTarget, \
    StaticText as wxStaticText, \
	TextCtrl as wxTextCtrl, \
    MessageDialog as wxMessageDialog, \
    NewId as wxNewId
from wx import \
    MAJOR_VERSION as wxMAJOR_VERSION, \
    MINOR_VERSION as wxMINOR_VERSION, \
    RELEASE_VERSION as wxRELEASE_VERSION, \
	TE_MULTILINE as wxTE_MULTILINE, \
	TE_READONLY as wxTE_READONLY, \
    EVT_BUTTON as wxEVT_BUTTON, \
    RIGHT as wxRIGHT, \
    LEFT as wxLEFT, \
    ALIGN_RIGHT as wxALIGN_RIGHT, \
    ALIGN_CENTER as wxALIGN_CENTER, \
    TOP as wxTOP, \
    BOTTOM as wxBOTTOM, \
    ALL as wxALL, \
    VERTICAL as wxVERTICAL, \
    HORIZONTAL as wxHORIZONTAL, \
    OK as wxOK, \
    ID_CANCEL as wxID_CANCEL
from wx.lib.docview import PathOnly

from dbr import GT, VERSION_STRING


ID_OVERWRITE = wxNewId()
ID_APPEND = wxNewId()

db_here = PathOnly(__file__).decode(u'utf-8')


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
    def __init__(self, parent, id=-1, title=GT(u'Overwrite?'), message=u''):
        wxDialog.__init__(self, parent, id, title)
        self.message = wxStaticText(self, -1, message)
        
        self.button_overwrite = wxButton(self, ID_OVERWRITE, GT(u'Overwrite'))
        self.button_append = wxButton(self, ID_APPEND, GT(u'Append'))
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
            raise ValueError(GT(u'Too many files'))
        text = open(filenames[0]).read()
        try:
            if (not TextIsEmpty(self.obj.GetValue())):
                overwrite = OverwriteDialog(self.obj, message = GT(u'The text area is not empty!'))
                id = overwrite.ShowModal()
                if (id == ID_OVERWRITE):
                    self.obj.SetValue(text)
                elif (id == ID_APPEND):
                    self.obj.SetInsertionPoint(-1)
                    self.obj.WriteText(text)
            else:
                self.obj.SetValue(text)
        except UnicodeDecodeError:
            wxMessageDialog(None, GT(u'Error decoding file'), GT(u'Error'), wxOK).ShowModal()


### -*- Checks if Text Control is Empty -*- ###
def TextIsEmpty(text):
    text = u''.join(u''.join(text.split(u' ')).split(u'\n'))
    return (text == u'')
