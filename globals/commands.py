# -*- coding: utf-8 -*-

## \package globals.commands
#  
#  Executable commands available from the system

# MIT licensing; See: docs/LICENSE.txt


from dbr.commandcheck import CommandExists


CMD_tar = CommandExists(u'tar')
CMD_md5sum = CommandExists(u'md5sum')
CMD_lintian = CommandExists(u'lintian')
CMD_gzip = CommandExists(u'gzip')
CMD_dpkg = CommandExists(u'dpkg')
CMD_gdebi = CommandExists(u'gdebi')
CMD_ar = CommandExists(u'ar')
CMD_bsdar = CommandExists(u'bsdar')

CMD_system_installer = None

# Set the system installer by priority
for C in CMD_gdebi, CMD_dpkg, CMD_bsdar, CMD_ar:
    if C:
        CMD_system_installer = C
        break
