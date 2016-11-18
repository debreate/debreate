#! /usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: This script is incomplete


import commands, errno, os, sys, time

from scripts_globals import GetInfoValue
from scripts_globals import required_locale_files
from scripts_globals import root_dir


# Updates the 'locale/debreate.pot' file
def UpdateMain():
    pass

for F in required_locale_files:
    if not os.path.isfile(F):
        print('[ERROR] Required file not found: {}'.format(F))
        sys.exit(errno.ENOENT)

FILE_pot = 'locale/debreate.pot'
YEAR = time.strftime('%Y')

PACKAGE = GetInfoValue('NAME')
AUTHOR = GetInfoValue('AUTHOR')
EMAIL = GetInfoValue('EMAIL')
VERSION = GetInfoValue('VERSION')

# Format
gt_language = '--language=Python'
gt_keyword = '--keyword=GT -k'

# Package
gt_author = '--copyright-holder="{}"'.format(AUTHOR)
gt_package = '--package-name={}'.format(PACKAGE.title())
gt_version = '--package-version={}'.format(VERSION)
gt_email = '--msgid-bugs-address={}'.format(EMAIL)

# Output
gt_domain = '--default-domain={}'.format(PACKAGE.lower())
gt_directory = '--directory="{}"'.format(root_dir)
gt_output = '-i -o {}'.format(FILE_pot)

# Misc
gt_other = '--no-location --no-wrap --sort-output'
#gt_other = '--no-wrap --sort-output'


args_format = ' '.join((gt_language, gt_keyword))
args_package = ' '.join((gt_author, gt_package, gt_version, gt_email))
args_output = ' '.join((gt_domain, gt_directory, gt_output))
args_misc = gt_other

cmd_gt = 'find ./ -name "*.py" | xargs xgettext {} {} {} {}'.format(
    args_format, args_package, args_output,
    args_misc
    )

cmd_output = commands.getstatusoutput(cmd_gt)
cmd_code = cmd_output[0]
cmd_output = cmd_output[1]

if cmd_code:
    print('An error occurred during Gettext output:\n')
    print(cmd_output)
    
    sys.exit(1)

print('\nGettext scan complete')

# Manual edits
if os.path.isfile(FILE_pot):
    print('\nExamining file contents ...')
    
    FILE_BUFFER = open(FILE_pot, 'r')
    pot_lines = FILE_BUFFER.read().split('\n')
    FILE_BUFFER.close()
    
    pot_lines_orig = tuple(pot_lines)
    
    # Used to bypass in case there are multiple lines with same contents
    language_line = False
    
    for L in pot_lines:
        line_index = pot_lines.index(L)
        
        # Only making changes to comment lines
        if L and L[0] == '#':
            if L.endswith('SOME DESCRIPTIVE TITLE.'):
                pot_lines[line_index] = L.replace('SOME DESCRIPTIVE TITLE.', 'Debreate - Debian Package Builder')
                continue
            
            elif L.startswith('# Copyright (C) YEAR'):
                pot_lines[line_index] = L.replace('Copyright (C) YEAR', 'Copyright © {}'.format(YEAR))
                continue
        
        elif not language_line and L.endswith('"Language: \\n"'):
            pot_lines[line_index] = L.replace('Language: \\n', 'Language: LANGUAGE\\n')
            language_line = True
            continue
    
    pot_lines.insert(4,
'#\n\
# NOTES:\n\
#   If "%s" or "{}" is in the msgid, be sure to put it in\n\
#   the msgstr or parts of Debreate will not function.\n\
#\n\
#   If you do not wish to translate a line just leave its\n\
#   msgstr blank')
    
    if tuple(pot_lines) != pot_lines_orig:
        print('\nMaking some adjustments ...')
        
        FILE_BUFFER = open(FILE_pot, 'w')
        FILE_BUFFER.write('\n'.join(pot_lines))
        FILE_BUFFER.close()
    
    print('\nFinished\n')
    
    sys.exit(0)

print('\nAn error occurred, could not locate Gettext .pot file: {}'.format(FILE_pot))
sys.exit(1)
