# -*- coding: utf-8 -*-

## \package globals.commands
#  
#  Executable commands available from the system

# MIT licensing
# See: docs/LICENSE.txt


import os, subprocess, wx
from subprocess import PIPE
from subprocess import STDOUT

from dbr.commandcheck       import CommandExists
from dbr.language           import GT
from globals.wizardhelper   import GetTopWindow


CMD_dpkgdeb = CommandExists(u'dpkg-deb')
CMD_fakeroot = CommandExists(u'fakeroot')

if not CMD_fakeroot:
    CMD_fakeroot = CommandExists(u'fakeroot-sysv')

CMD_gdebi = CommandExists(u'gdebi')
CMD_gdebi_gui = CommandExists(u'gdebi-gtk')
CMD_gvfs_trash = CommandExists(u'gvfs-trash')
CMD_gzip = CommandExists(u'gzip')
CMD_lintian = CommandExists(u'lintian')
CMD_md5sum = CommandExists(u'md5sum')
CMD_sudo = CommandExists(u'sudo')
CMD_tar = CommandExists(u'tar')
CMD_xdg_open = CommandExists(u'xdg-open')

# Check for gdebi KDE frontend of Gtk not available
if not CMD_gdebi_gui:
    CMD_gdebi_gui = CommandExists(u'gdebi-kde')

CMD_system_packager = None

# Order in priority
CMDS_packagers = (
    CMD_dpkgdeb,
)

# Sets the system packager by priority
for C in CMDS_packagers:
    if C:
        CMD_system_packager = C
        break


## TODO: Doxygen
def ExecuteCommand(cmd, args=[], elevate=False, pword=wx.EmptyString):
    if elevate and pword.strip(u' \t\n') == wx.EmptyString:
        return (None, GT(u'Empty password'))
    
    CMD_sudo = GetExecutable(u'sudo')
    
    if not CMD_sudo:
        return (None, GT(u'Super user command (sudo) not available'))
    
    main_window = GetTopWindow()
    
    if isinstance(args, (unicode, str)):
        cmd_line = [args,]
    
    else:
        cmd_line = list(args)
    
    cmd_line.insert(0, cmd)
    
    main_window.Enable(False)
    
    # FIXME: Better way to execute commands
    if elevate:
        cmd_line.insert(0, u'sudo')
        cmd_line.insert(1, u'-S')
        
        cmd_line = u' '.join(cmd_line)
        
        cmd_output = os.popen(u'echo {} | {}'.format(pword, cmd_line)).read()
    
    else:
        cmd_output = subprocess.Popen(cmd_line, stdout=PIPE, stderr=PIPE)
        cmd_output.wait()
    
    main_window.Enable(True)
    
    stdout = wx.EmptyString
    
    if isinstance(cmd_output, subprocess.Popen):
        if cmd_output.stdout:
            stdout = cmd_output.stdout
        
        if cmd_output.stderr:
            if stdout == wx.EmptyString:
                stdout = cmd_output.stderr
            
            else:
                stdout = u'{}\n{}'.format(stdout, cmd_output.stderr)
        
        returncode = cmd_output.returncode
    
    else:
        stdout = cmd_output
        returncode = 0
    
    return (returncode, stdout)


## TODO: Doxygen
def GetCommandOutput(cmd, args=[]):
    command_line = list(args)
    command_line.insert(0, cmd)
    
    output = subprocess.Popen(command_line, stdout=PIPE, stderr=STDOUT).communicate()[0]
    
    # The Popen command adds a newline character at end of output
    return output.rstrip(u'\n')


## Retrieves executable it exists on system
def GetExecutable(cmd):
    alternatives = {
        u'fakeroot': u'fakeroot-sysv', 
        }
    
    found_command = CommandExists(cmd)
    
    if not found_command and cmd in alternatives:
        if isinstance(alternatives[cmd], (unicode, str)):
            found_command = alternatives[cmd]
        
        else:
            for ALT in alternatives[cmd]:
                found_command = CommandExists(ALT)
                if found_command:
                    break
    
    return found_command


def GetSystemInstaller():
    system_installer = GetExecutable(u'gdebi-gtk')
    
    if not system_installer:
        system_installer = GetExecutable(u'gdebi-kde')
    
    return system_installer
