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
