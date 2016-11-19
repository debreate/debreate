# -*- coding: utf-8 -*-

## \package globals.commands
#  
#  Executable commands available from the system

# MIT licensing; See: docs/LICENSE.txt


from dbr.commandcheck import CommandExists


CMD_ar = CommandExists(u'ar')
CMD_bsdar = CommandExists(u'bsdar')
CMD_dpkg = CommandExists(u'dpkg')
CMD_dpkgdeb = CommandExists(u'dpkg-deb')
CMD_fakeroot = CommandExists(u'fakeroot')
CMD_gdebi = CommandExists(u'gdebi')
CMD_gdebi_gui = CommandExists(u'gdebi-gtk')
CMD_gzip = CommandExists(u'gzip')
CMD_lintian = CommandExists(u'lintian')
CMD_md5sum = CommandExists(u'md5sum')
CMD_tar = CommandExists(u'tar')
CMD_xdg_open = CommandExists(u'xdg-open')

# Check for gdebi KDE frontend of Gtk not available
if not CMD_gdebi_gui:
    CMD_gdebi_gui = CommandExists(u'gdebi-kde')

CMD_system_installer = None

# Order in priority
CMDS_installers = (
    CMD_gdebi_gui,
    CMD_gdebi,
    CMD_dpkg,
)

# Sets the system installer by priority
for C in CMDS_installers:
    if C:
        CMD_system_installer = C
        break

CMD_system_packager = None

# Order in priority
CMDS_packagers = (
    CMD_dpkgdeb,
    CMD_bsdar,
    CMD_ar,
)

# Sets the system packager by priority
for C in CMDS_packagers:
    if C:
        CMD_system_packager = C
        break
