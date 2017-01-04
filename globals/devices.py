# -*- coding: utf-8 -*-

## \package globals.devices

# MIT licensing
# See: docs/LICENSE.txt


import os

from dbr.log        import Logger
from globals.fileio import ReadFile
from globals.paths  import ConcatPaths


## Class that represents a mounted storage device
class StorageDevice:
    def __init__(self, node, mount_point):
        self.Node = node
        self.MountPoint = mount_point
        
        self.Label = None
        
        label_dir = u'/dev/disk/by-label'
        if os.path.isdir(label_dir):
            for LABEL in os.listdir(label_dir):
                link = ConcatPaths((label_dir, LABEL))
                
                if os.path.islink(link):
                    link_node = os.path.realpath(link)
                    if link_node == self.Node:
                        Logger.Debug(__name__, u'Found label for {}: {}'.format(self.Node, LABEL))
                        
                        self.Label = LABEL
                        break
        
        # As last resort just use mount point basename
        if not self.Label:
            if mount_point == u'/':
                self.Label = mount_point
            
            else:
                self.Label = os.path.basename(mount_point)
        
        device_types = {
            u'/dev/sd': u'hard-disk',
            u'/dev/hd': u'hard-disk',
            u'/dev/pd': u'hard-disk',
            u'/dev/fd': u'floppy',
            }
        
        # The type string is used in dbr.tree.DirectroyTree to set item icon
        self.Type = None
        
        for TYPE in device_types:
            if node.startswith(TYPE):
                self.Type = device_types[TYPE]
    
    
    ## Get the instances string mount point
    def GetMountPoint(self):
        return self.MountPoint


## Opens /etc/mtab file & parses attached storage devices
#  
#  \return
#    \b \e Dictionary of device labels with mount points
def ParseMountedDevices():
    # FIXME: Identify labels for different systems & drive types
    device_labels = (
        u'/dev/sd',
        )
    
    # Empty the device list
    mounted_devices = {}
    
    if os.path.isfile(u'/etc/mtab'):
        mtab = ReadFile(u'/etc/mtab', split=True, convert=list)
        
        # Only keep lines referring to devices directory
        for X in reversed(range(len(mtab))):
            if not mtab[X].startswith(u'/dev'):
                mtab.pop(X)
        
        mtab.sort()
        
        for LINE in mtab:
            LINE = LINE.split(u' ')
            
            device = LINE[0]
            mount_point = LINE[1]
            
            for LABEL in device_labels:
                if device.startswith(LABEL):
                    mounted_devices[device] = mount_point
    
    else:
        Logger.Warning(__name__, u'/etc/mtab file does not exist. Mounted devices list will be empty')
    
    return mounted_devices


## Retrieves a list of globals.devices.StorageDevice instances
def GetMountedStorageDevices():
    mounted_devices = ParseMountedDevices()
    
    device_list = []
    
    for DEV in sorted(mounted_devices):
        device_list.append(StorageDevice(DEV, mounted_devices[DEV]))
    
    #device_list.sort(key=StorageDevice.GetMountPoint)
    
    return tuple(sorted(device_list, key=StorageDevice.GetMountPoint))
