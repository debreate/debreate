# -*- coding: utf-8 -*-

## \package globals.fileitem

# MIT licensing
# See: docs/LICENSE.txt


import os

from dbr.colors         import COLOR_dir
from dbr.colors         import COLOR_executable
from dbr.colors         import COLOR_link
from globals.fileio     import GetTimestamp
from globals.fileio     import ReadFile
from globals.strings    import IsString
from globals.strings    import TextIsEmpty


## TODO: Doxygen
class FileType:
    NORM = None
    EXEC = COLOR_executable
    LINK = COLOR_link
    DIR = COLOR_dir


## An object that represents a file
class FileItem:
    def __init__(self, path, target=None):
        self.Path = path
        self.Target = target
        
        # Timestamp is set at construction
        self.Timestamp = GetTimestamp(self.Path)
        
        # Defaults to normal file
        self.Type = FileType.NORM
        
        self.SetType()
    
    
    ## Checks if the file exists on the filesystem
    def Exists(self):
        return os.path.isfile(self.Path)
    
    
    ## Retrieves file's basename
    def GetBasename(self):
        return os.path.basename(self.Path)
    
    
    ## Retrieves file's full path
    def GetPath(self):
        return self.Path
    
    
    ## Retrieves file's target directory
    def GetTarget(self):
        return self.Target
    
    
    ## Retrieves the file's timestamp from memory
    #
    #  NOTE: May differ from actual timestamp
    #        Call 'TimestampChanged' to update
    def GetTimestamp(self):
        return self.Timestamp
    
    
    ## Retrieves the file type (normal file, directory, symbolic link, or executable)
    def GetType(self):
        return self.Type
    
    
    ## Checks if the file has a target installation directory
    def HasTarget(self):
        return IsString(self.Target) and not TextIsEmpty(self.Target)
    
    
    ## Checks if the item represented is a directory
    def IsDirectory(self):
        return os.path.isdir(self.Path)
    
    
    ## Checks if the item represented is a regular file
    def IsFile(self):
        return os.path.isfile(self.Path)
    
    
    ## Checks if file is executable
    def IsExecutable(self):
        if self.IsFile():
            return os.access(self.Path, os.X_OK)
        
        return False
    
    
    ## Reads file's contents into memory
    #
    #  \param split
    #    If \b \e True, splits the text into a list
    #  \param convert
    #    Type of list to split contents into (can be \b \e tuple or \b \e list)
    #    FIXME: Use boolean???
    #  \param noStrip
    #    \b \e String of leading & trailing characters to not strip
    def Read(self, split=False, convert=tuple, noStrip=None):
        return ReadFile(self.Path, split, convert, noStrip)
    
    
    ## Sets file's path & basename
    def SetPath(self, path):
        self.Path = path
    
    
    ## Sets file's target directory
    def SetTarget(self, target):
        self.Target = target
    
    
    ## Sets file type
    def SetType(self):
        if os.path.isdir(self.Path):
            self.Type = FileType.DIR
        
        elif os.path.islink(self.Path):
            self.Type = FileType.LINK
        
        elif os.access(self.Path, os.X_OK):
            self.Type = FileType.EXEC
    
    
    ## Checks if timestamp has been modified & updates
    def TimestampChanged(self):
        # Set file's timestamp if not already done
        if not self.Timestamp:
            self.Timestamp = GetTimestamp(self.Path)
            
            return False
        
        current_stamp = GetTimestamp(self.Path)
        
        if current_stamp != self.Timestamp:
            self.Timestamp = current_stamp
            
            return True
        
        return False
