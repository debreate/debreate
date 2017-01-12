# -*- coding: utf-8 -*-

## \package globals.commands
#  
#  Executable commands available from the system

# MIT licensing; See: docs/LICENSE.txt


import os, subprocess, wx
from subprocess import PIPE
from subprocess import STDOUT

from dbr.commandcheck   import CommandExists
from dbr.language       import GT


CMD_dpkgdeb = CommandExists(u'dpkg-deb')
CMD_fakeroot = CommandExists(u'fakeroot')

if not CMD_fakeroot:
    CMD_fakeroot = CommandExists(u'fakeroot-sysv')

CMD_lintian = CommandExists(u'lintian')
CMD_md5sum = CommandExists(u'md5sum')
CMD_strip = CommandExists(u'strip')
CMD_tar = CommandExists(u'tar')
CMD_trash = CommandExists(u'gvfs-trash')
CMD_xdg_open = CommandExists(u'xdg-open')

CMD_system_packager = CMD_dpkgdeb


## TODO: Doxygen
def ExecuteCommand(cmd, args=[], elevate=False, pword=wx.EmptyString):
    if elevate and pword.strip(u' \t\n') == wx.EmptyString:
        return (None, GT(u'Empty password'))
    
    CMD_sudo = GetExecutable(u'sudo')
    
    if not CMD_sudo:
        return (None, GT(u'Super user command (sudo) not available'))
    
    main_window = wx.GetApp().GetTopWindow()
    
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
    return CommandExists(cmd)


def GetSystemInstaller():
    system_installer = GetExecutable(u'gdebi-gtk')
    
    if not system_installer:
        system_installer = GetExecutable(u'gdebi-kde')
    
    return system_installer
