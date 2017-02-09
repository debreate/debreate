#! /usr/bin/env python
# -*- coding: utf-8 -*-

# MIT licensing
# See: docs/LICENSE.txt


import commands, errno, os, subprocess, sys, time

from scripts_globals import ConcatPaths
from scripts_globals import GetInfoValue
from scripts_globals import required_locale_files
from scripts_globals import DIR_root


# FIXME: This script used the deprecated module 'commands'


for F in required_locale_files:
    if not os.path.isfile(F):
        print('[ERROR] Required file not found: {}'.format(F))
        sys.exit(errno.ENOENT)

DIR_locale = ConcatPaths(DIR_root, 'locale')

if not os.path.isdir(DIR_locale):
    print('ERROR: Locale directory does not exist: {}'.format(DIR_locale))
    sys.exit(1)


if sys.argv[1:]:
    cmd = sys.argv[1]
    if cmd.lower() == 'compile':
        print('\nCompiling locales ...')
        
        #gt_sources = []
        for ROOT, DIRS, FILES in os.walk(DIR_locale):
            for source_file in FILES:
                if source_file.endswith('.po'):
                    base_name = source_file.rstrip('.po')
                    
                    target_dir = ConcatPaths(ROOT, 'LC_MESSAGES')
                    
                    source_file = ConcatPaths(ROOT, source_file)
                    
                    target_file = ConcatPaths(target_dir, '{}.mo'.format(base_name))
                    
                    if os.path.isfile(source_file):
                        if not os.path.isdir(target_dir):
                            os.makedirs(target_dir)
                        
                        print('\nCompiling: {} -> {}'.format(source_file, target_file))
                        fmt_output = subprocess.Popen(['msgfmt', source_file, '-o', target_file])
        
        print
        sys.exit(0)
    
    print('ERROR: Unknown command: {}'.format(cmd))
    sys.exit(1)


FILE_pot = ConcatPaths(DIR_locale, 'debreate.pot')
YEAR = time.strftime('%Y')

# Make sure we are using a clean slate
if os.path.isfile(FILE_pot):
    if not os.access(FILE_pot, os.W_OK):
        print('ERROR: .pot file exists & is not writable: {}'.format(FILE_pot))
        sys.exit(1)
    
    os.remove(FILE_pot)

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
gt_directory = '--directory="{}"'.format(DIR_root)
gt_output = '-i -o {}'.format(FILE_pot)

# Misc
gt_other = '--no-wrap --sort-output'


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
    
    NOTES = '#\n\
# NOTES:\n\
#   If "%s" or "{}" is in the msgid, be sure to put it in\n\
#   the msgstr or parts of Debreate will not function.\n\
#\n\
#   If you do not wish to translate a line just leave its\n\
#   msgstr blank'

    
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
    
    pot_lines.insert(4, NOTES)
    
    if tuple(pot_lines) != pot_lines_orig:
        print('\nMaking some adjustments ...')
        
        FILE_BUFFER = open(FILE_pot, 'w')
        FILE_BUFFER.write('\n'.join(pot_lines))
        FILE_BUFFER.close()
    
    print('\nMerging locales ...')
    
    for ROOT, DIRS, FILES in os.walk(DIR_locale):
        for F in FILES:
            if F.endswith('.po'):
                F = '{}/{}'.format(ROOT, F)
                language = F.split('/')[1]
                
                print('\nLanguage: {}'.format(language))
                print('File: {}'.format(F))
                
                commands.getstatusoutput('msgmerge -U -i -s -N --no-location --no-wrap --backup=none --previous "{}" "{}"'.format(F, FILE_pot))
                
                FILE_BUFFER = open(F, 'r')
                po_data = FILE_BUFFER.read()
                FILE_BUFFER.close()
                
                if 'Project-Id-Version: Debreate' in po_data:
                    po_lines = po_data.split('\n')
                    po_lines_orig = tuple(po_lines)
                    
                    for L in po_lines:
                        line_index = po_lines.index(L)
                        if 'Project-Id-Version: Debreate' in L:
                            L = L.split(' ')
                            L[-1] = '{}\\n"'.format(VERSION)
                            L = ' '.join(L)
                            
                            po_lines[line_index] = L
                            
                            # No need to continue checking lines
                            break
                    
                    if NOTES not in '\n'.join(po_lines):
                        po_lines.insert(4, NOTES)
                    
                    if tuple(po_lines) != po_lines_orig:
                        FILE_BUFFER = open(F, 'w')
                        FILE_BUFFER.write('\n'.join(po_lines))
                        FILE_BUFFER.close()
    
    print('\nFinished\n')
    
    sys.exit(0)

print('\nAn error occurred, could not locate Gettext .pot file: {}'.format(FILE_pot))
sys.exit(1)
