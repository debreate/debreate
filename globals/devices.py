
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module globals.devices

import os

from libdbr.fileio import readFile
from libdbr.logger import Logger
from libdbr.paths  import getSystemRoot


logger = Logger(__name__)

## Class that represents a mounted storage device.
class StorageDevice:
  def __init__(self, node, mount_point):
    self.Node = node
    self.MountPoint = mount_point

    self.Label = None

    label_dir = "/dev/disk/by-label"
    if os.path.isdir(label_dir):
      for LABEL in os.listdir(label_dir):
        link = os.path.join(label_dir, LABEL)

        if os.path.islink(link):
          link_node = os.path.realpath(link)
          if link_node == self.Node:
            logger.debug("Found label for {}: {}".format(self.Node, LABEL))

            self.Label = LABEL
            break

    # As last resort just use mount point basename
    if not self.Label:
      if mount_point == getSystemRoot():
        self.Label = mount_point

      else:
        self.Label = os.path.basename(mount_point)

    device_types = {
      "/dev/sd": "drive-fixed",
      "/dev/hd": "drive-fixed",
      "/dev/pd": "drive-fixed",
      "/dev/fd": "drive-floppy",
      }

    # The type string is used in ui.tree.DirectroyTree to set item icon
    self.Type = None

    for TYPE in device_types:
      if node.startswith(TYPE):
        self.Type = device_types[TYPE]
        break

    # Extended device type check
    # ???: Better method?
    type_dir = "/dev/disk/by-path"
    if os.path.isdir(type_dir):
      node_types = os.listdir(type_dir)
      for TYPE in node_types:
        link = os.path.join(type_dir, TYPE)

        if os.path.islink(link):
          link_node = os.path.realpath(link)

          if link_node == self.Node:
            # Ensure we are only dealing with lowercase
            TYPE = TYPE.lower()

            if "usb" in TYPE.split("-"):
              logger.debug("{} is a removable drive".format(self.Node))
              self.Type = "removable"

  ## Get the instances string mount point
  def GetMountPoint(self):
    return self.MountPoint


## Opens /etc/mtab file & parses attached storage devices.
#
#  @return
#    Dictionary of device labels with mount points.
def ParseMountedDevices():
  # FIXME: Identify labels for different systems & drive types
  device_labels = (
    "/dev/sd",
    )

  # Empty the device list
  mounted_devices = {}

  if os.path.isfile("/etc/mtab"):
    mtab = readFile("/etc/mtab").split("\n")

    # Only keep lines referring to devices directory
    for X in reversed(range(len(mtab))):
      if not mtab[X].startswith("/dev"):
        mtab.pop(X)

    mtab.sort()

    for LINE in mtab:
      LINE = LINE.split(" ")

      device = LINE[0]
      mount_point = LINE[1]

      for LABEL in device_labels:
        if device.startswith(LABEL):
          mounted_devices[device] = mount_point
  else:
    logger.warn("/etc/mtab file does not exist. Mounted devices list will be empty")

  return mounted_devices


## Retrieves a list of globals.devices.StorageDevice instances.
def GetMountedStorageDevices():
  mounted_devices = ParseMountedDevices()

  device_list = []

  for DEV in sorted(mounted_devices):
    device_list.append(StorageDevice(DEV, mounted_devices[DEV]))

  #device_list.sort(key=StorageDevice.GetMountPoint)

  return tuple(sorted(device_list, key=StorageDevice.GetMountPoint))
