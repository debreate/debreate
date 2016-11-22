# -*- coding: utf-8 -*-


import os, wx

from dbr.language   import GT
from dbr.pathctrl   import PATH_DEFAULT
from dbr.pathctrl   import PATH_WARN
from dbr.pathctrl   import PathCtrl
from globals.paths  import PATH_app


ID_BIN = wx.NewId()
ID_SRC = wx.NewId()
ID_DSC = wx.NewId()
ID_CNG = wx.NewId()


# Colors depicting importance of fields
Mandatory = (255,200,192)
Recommended = (197,204,255)
Optional = (255,255,255)
Unused = (200,200,200)
Disabled = (246, 246, 245)


# Get Home directory
homedir = os.getenv(u'HOME')

# Icons
ICON_ERROR = u'{}/bitmaps/error64.png'.format(PATH_app)
ICON_INFORMATION = u'{}/bitmaps/question64.png'.format(PATH_app)


# Path text controls
PathCtrl = PathCtrl
PATH_DEFAULT = PATH_DEFAULT
PATH_WARN = PATH_WARN


# *** File/Folder Dialogs *** #

class DBDialog(wx.Dialog):
    """A custom dialog for opening/saving files and folders"""
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, style=wx.DEFAULT_DIALOG_STYLE, size=(350,450))
        
#		self.SetTitle(u'Browse for a Folder')
        
        # IDs for context menu and buttons
        ID_Folder = 100
        ID_Rename = 101
        ID_Delete = 102
        
        
        # Context menu
        self.menu = wx.Menu()
        self.menu.Append(ID_Folder, GT(u'New Folder'))
        self.menu.Append(ID_Rename, GT(u'Rename'))
        self.menu.AppendSeparator()
        self.menu.Append(ID_Delete, GT(u'Move to Trash'))
        
        wx.EVT_MENU(self, ID_Folder, self.CreateFolder)
        wx.EVT_MENU(self, ID_Rename, self.ShowRename)
        wx.EVT_MENU(self, ID_Delete, self.Delete)
        
#		# Display area
#		self.dir_tree = wx.GenericDirCtrl(self, -1, os.getcwd())
#		
#		# Add a context menu to the dir_tree
#		self.dir_tree.Bind(wx.EVT_CONTEXT_MENU, self.OnContext)
        
        # Buttons
        self.New = wx.Button(self, ID_Folder, GT(u'New Folder'))
        self.Ok = wx.Button(self, wx.OK)
        self.Cancel = wx.Button(self, wx.CANCEL, GT(u'Cancel'))
        
        wx.EVT_BUTTON(self.New, -1, self.CreateFolder)
        wx.EVT_BUTTON(self.Ok, -1, self.OnButton)
        wx.EVT_BUTTON(self.Cancel, -1, self.OnButton)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.New, 0, wx.ALL, 5)
        button_sizer.AddSpacer(40)
        button_sizer.Add(self.Ok, 0, wx.ALL, 5)
        button_sizer.Add(self.Cancel, 0, wx.ALL, 5)
        
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        #self.main_sizer.Add(self.dir_tree, 1, wx.EXPAND|wx.ALL, 20)
        self.main_sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT, 16)
        
        self.SetAutoLayout(True)
        self.SetSizer(self.main_sizer)
        self.Layout()
        
        
        self.value = False
        
    
    
    def SetType(self, type, mode):
        if type.lower() == u'file':
            try:
                self.dir_tree = wx.GenericDirCtrl(self, -1, os.getcwd(), filter=u'*', style=wx.DIRCTRL_SHOW_FILTERS)
            except OSError:
                self.dir_tree = wx.GenericDirCtrl(self, -1, os.getenv(u'HOME'), filter=u'*', style=wx.DIRCTRL_SHOW_FILTERS)
            if mode.lower() == u'save':
                self.Ok.SetLabel(GT(u'Save'))
            elif mode.lower() == u'open':
                self.Ok.SetLabel(GT(u'Open'))
        elif type.lower() == u'dir':
            self.dir_tree = wx.GenericDirCtrl(self, -1, os.getcwd(),
                    style=wx.DIRCTRL_DIR_ONLY|wx.BORDER_SIMPLE)
            if mode.lower() == u'save':
                self.Ok.SetLabel(GT(u'Save'))
            elif mode.lower() == u'open':
                self.Ok.SetLabel(GT(u'Open'))
        
        # Add a context menu to the dir_tree
        self.dir_tree.Bind(wx.EVT_CONTEXT_MENU, self.OnContext)
        # Add to main sizer
        self.main_sizer.Insert(0, self.dir_tree, 1, wx.EXPAND|wx.ALL, 20)
    
    def DisplayModal(self):
        self.ShowModal()
        return self.value
        
    def OnContext(self, event):
        # Get folder/file that is highlighted
        selected = self.dir_tree.GetPath()
        
        # Show the context menu
        self.dir_tree.PopupMenu(self.menu)
    
    def GetPath(self):
        return self.dir_tree.GetPath()
        
    def OnButton(self, event):
        id = event.GetEventObject().GetId()
        
        dest_path = self.dir_tree.GetPath()
        
        if id == wx.OK:
            if os.path.isdir(dest_path):
                os.chdir(dest_path)
            else:
                os.chdir(os.path.split(dest_path)[0])
            self.value = True
        self.Close()
    
    def SetFilter(self, filter):
        self.dir_tree.SetFilter(filter)
        self.dir_tree.ReCreateTree()
    
    def CreateFolder(self, event):
        # Creates a new folder in the highlighted path
        destination = self.dir_tree.GetPath()
        
        # If highlighted path is folder, create new folder in path
        n = GT(u'New Folder')
        if os.path.isdir(destination):
            new_folder = u'{}/{}'.format(destination, n)
        # If highlighted path is file, create new folder in the same directory
        else:
            parent_dir = os.path.split(destination)[0]
            new_folder = u'{}/{}'.format(parent_dir, n)
        
        folder_number = 0
        unavailable = True
        while unavailable:
            # First check to see if "New Folder" already exists in target path
            # If it does exist, create folders with numerical value "1", "2", etc.
            try:
                if not os.path.exists(new_folder):
                    os.mkdir(new_folder)
                    unavailable = False
                elif os.path.exists(new_folder):
                    folder_number += 1
                    new_folder = u'{}/{} ({})'.format(destination, n, folder_number)
            # If folder can't be created show error dialog
            except OSError:
                unavailable = False
                permission_error = wx.MessageDialog(self, GT(u'Permission Denied'), GT(u'Error'), wx.OK|wx.ICON_EXCLAMATION)
                permission_error.ShowModal()
        
        # Refresh the tree so that the new folders are dislplayed
        self.dir_tree.ReCreateTree()
        # When tree is refreshed return to new folder
        self.dir_tree.SetPath(new_folder)

    
    def Delete(self, event):
        path = self.dir_tree.GetPath()
        
        # Get the parent dir of the file/folder being deleted
        parent_path = os.path.split(path)[0]
        
        # Move file to trash
        os.system((u'gvfs-trash "{}"'.format(path)))
        
        self.dir_tree.ReCreateTree()
        self.dir_tree.SetPath(parent_path)
    
    def ShowRename(self, event):
        # Get the filename to be placed in the textarea
        filename = os.path.split(self.dir_tree.GetPath())[1]
        
        # Create the rename dialog
        dia = wx.Dialog(self, -1, GT(u'Rename'), size=(200,75))
        
        # Create the input area
        input = wx.TextCtrl(dia, -1, filename)
        
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        input_sizer.Add(input, 1)
        
        # Two buttons to confirm/cancel renaming
        button_rename = wx.Button(dia, wx.WXK_RETURN, GT(u'Rename'))
        button_cancel = wx.Button(dia, wx.WXK_ESCAPE, GT(u'Cancel'))
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddMany([(button_rename, 0, wx.ALL, 5), (button_cancel, 0, wx.ALL, 5)])
        
        # If button_rename pressed, rename file, otherwise leave as is, and close dialog
        def Rename(event):
            try:
                id = event.GetKeyCode()
            except:
                id = event.GetId()
            # Get potential name
            name = input.GetValue()
            
            # Get the selected path to folder/file
            path = self.dir_tree.GetPath()
            
            # Set the path and name
            new_name = u'{}/{}'.format(os.path.split(path)[0], name)
            
            if id == wx.WXK_RETURN or id == wx.WXK_NUMPAD_ENTER:
                if os.path.isdir(new_name) or os.path.isfile(new_name):
                    direrr = wx.MessageDialog(dia, GT(u'Name already used in current directory'), GT(u'Error'),
                                wx.OK|wx.ICON_EXCLAMATION)
                    direrr.ShowModal()
                    direrr.Close()
                else:
                    os.rename(path, new_name)
                    
                    # Return to renamed folder/file
                    self.dir_tree.ReCreateTree()
                    self.dir_tree.SetPath(new_name)
                    dia.Close()
            elif id == wx.WXK_ESCAPE:
                dia.Close()
            event.Skip()
        
        
        wx.EVT_BUTTON(button_rename, wx.WXK_RETURN, Rename)
        wx.EVT_BUTTON(button_cancel, -1, Rename)
        wx.EVT_KEY_DOWN(input, Rename)
        
        # Set layout for rename dialog
        naming_sizer = wx.BoxSizer(wx.VERTICAL)
        naming_sizer.Add(input_sizer, 1, wx.EXPAND|wx.ALL, 5)
        naming_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER)
        
        dia.SetAutoLayout(True)
        dia.SetSizer(naming_sizer)
        dia.Layout()
        
        # Set focus on text area for quick renaming
        input.SetFocus()
        
        # Show the dialog
        dia.ShowModal()
        dia.Destroy()
        


class OpenDir(DBDialog):
    def __init__(self, parent, title=GT(u'Choose Directory')):
        DBDialog.__init__(self, parent, title)
        
        self.SetTitle(title)
        
        self.SetType(u'dIr', u'OpeN')
        


class OpenFile(DBDialog):
    def __init__(self, parent, title=GT(u'Open File')):
        DBDialog.__init__(self, parent, title)
        
        self.SetTitle(title)
        
        self.SetType(u'FilE', u'oPeN')
        
        # Find the wx.TreeCtrl child so events can be passed to it
        self.tree = self.dir_tree.GetChildren()[0]
        
        # Add an event handler to the tree for opening files on double-click
        wx.EVT_LEFT_DCLICK(self.tree, self.OnDClick)
    
    def OnDClick(self, event):
        path = self.dir_tree.GetPath()
        if os.path.isfile(path):
            self.OnButton(wx.OK)
        event.Skip()
        
    def OnButton(self, event):
        try:
            id = event.GetEventObject().GetId()  # Get the button that was pressed
        except AttributeError:
            id = event  # Use this if a EVT_LEFT_DCLICK is processed
        
        # Get the current selected path and (since is a file) get the parent path to return to after
        # file is selected
        path = self.dir_tree.GetPath()
        parent_path = os.path.split(path)[0]
        
        if id == wx.OK:
            # If the selected path is a file, confirm and close, otherwise try to expand the path
            if os.path.isfile(path):
                os.chdir(parent_path)
                self.value = True
                self.Close()
            elif os.path.isdir(path):
                self.dir_tree.ExpandPath(path)
        # If cancel is pressed, just close the dialog
        else:
            self.Close()


class SaveFile(DBDialog):
    def __init__(self, parent, title=GT(u'Save File'), defaultExtension=None):
        DBDialog.__init__(self, parent, title)
        
        self.defaultExtension = defaultExtension
        
        self.SetTitle(title)
        
        self.SetType(u'FILE', u'savE')
        
        # Find the wx.TreeCtrl child so events can be passed to it
        self.tree = self.dir_tree.GetChildren()[0]
        
        self.TextCtrl = wx.TextCtrl(self, -1)
        wx.EVT_KEY_DOWN(self.TextCtrl, self.OnButton)
        
        # Double-click is the same as "Save"
        wx.EVT_LEFT_DCLICK(self.tree, self.OnButton)
        
        # Put the cursor in the text control when the dialog is shown
        wx.EVT_INIT_DIALOG(self, self.OnSelfShow)
        
        # Invalid characters at beginning of filename
        self.invalid_first_char = (u' u', u'.')
        # Invalid characters in filename
        self.invalid_char = (u'/', u'/')
        
        self.main_sizer.Insert(1, self.TextCtrl, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 20)
        
        def OnLMouseButton(event):
            path = self.dir_tree.GetPath()
            if os.path.isfile(path):
                self.SetFilename(self.dir_tree.GetPath())
            event.Skip()
        wx.EVT_LEFT_UP(self.dir_tree.GetChildren()[0], OnLMouseButton)
    
    def OnSelfShow(self, event):
        self.TextCtrl.SetFocus()
    
    def SetFilename(self, path):
        filename = os.path.split(path)[1]
        self.TextCtrl.SetValue(filename)
    
    def GetFilename(self):
        return self.TextCtrl.GetValue()
    
    def GetPath(self):
        if os.path.isdir(self.dir_tree.GetPath()):
            return self.dir_tree.GetPath()
        else:
            return os.path.split(self.dir_tree.GetPath())[0]
    
    def OnButton(self, event):
        save_ids = (wx.OK, wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, 7000) # 7000 is for left mouse button d-click
        cancel_ids = (wx.CANCEL, wx.WXK_ESCAPE)
        try:
            id = event.GetKeyCode()
        except AttributeError:
            id = event.GetEventObject().GetId()
        
        # Find out if the selected path is a file or directory
        if os.path.isdir(self.dir_tree.GetPath()):
            dest_path = self.dir_tree.GetPath()
        else:
            # If the path is a file, set dest_path to dir where file resides
            dest_path = os.path.split(self.dir_tree.GetPath())[0]
        
        if id in save_ids:
            good_filename = True # Continue if the filename is okay
            filename = self.TextCtrl.GetValue()
            bad_filename_dia = wx.MessageDialog(self, GT(u'Bad File Name'), GT(u'Error'), wx.OK|wx.ICON_ERROR)
            # Check to see that the input value isn't empty
#			if self.TextCtrl.GetValue() == wx.EmptyString:
            if filename == wx.EmptyString or filename[0] in self.invalid_first_char:
                good_filename = False
                bad_filename_dia.ShowModal()
                #dia.Destroy()
            
            if good_filename:
                for char in filename:
                    if char in self.invalid_char:
                        good_filename = False
                        bad_filename_dia.ShowModal()
            
            if good_filename:
                # If a default file extension is set add it to the filename
                if self.defaultExtension:
                    if self.TextCtrl.GetValue().split(u'.')[-1] != self.defaultExtension:
                        self.TextCtrl.SetValue(u'{}.{}'.format(self.TextCtrl.GetValue(), self.defaultExtension))
                # Set the Dir and Filename for saving
                savefile = u'{}/{}'.format(dest_path, self.TextCtrl.GetValue())
                
                # If everything checks out OK run this function
                def SaveIt():
                    if os.path.isdir(dest_path):
                        os.chdir(dest_path)
                    else:
                        os.chdir(os.path.split(dest_path)[0])
                    self.value = True
                    self.Close()
                
                if os.path.exists(savefile):
                    warn = wx.MessageDialog(self, GT(u'Overwrite File?'), GT(u'File Exists'), wx.YES_NO|wx.NO_DEFAULT)
                    if warn.ShowModal() == wx.ID_YES:
                        SaveIt()
                    warn.Destroy()
                else:
                    SaveIt()
        elif id in cancel_ids:
            self.Close()
        event.Skip()
