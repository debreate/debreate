#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MIT licensing
# See: docs/LICENSE.txt


import os, re, sys

from scripts_globals import ConcatPaths
from scripts_globals import lprint
from scripts_globals import root_dir


# Regular expression patterns used to extract substrings
#pattern = r'[\'"](.+?[^\\\'\\"\\])[\'"]'
#pattern = r'[\'"](.+?)[\'"]'
#pattern1 = r'\'(.+?[^\\\'\\])\''
pattern1 = r'\'(.+?)\''
#pattern2 = r'\"(.+?[^\"\\])\"'
pattern2 = r'\"(.+?)\"'

# Characters/Strings to be replaced in source code
# 
#    original: (replacement, (exclude-file-list))
replacements = {
    ' -> ': (' ➜ ', ('build', 'files',)),
    ' (C) ': (' © ',),
    ' (c) ': (' © ',),
    }

# For running test without risk of making changes to regular files
TESTING = False

if TESTING:
    test_file = ConcatPaths(root_dir, 'test.py')
    
    if not os.path.isfile(test_file):
        FILE_BUFFER = open(test_file, 'w')
        FILE_BUFFER.write('\n\
arrow1 = \' -> "sub-sub"\'\n\n\
arrow2 = \'  -> \'\n\n\
arrow3 = \' ->\'\n\n\
arrow4 = \'-> \'\n\n\
arrow5 = "  ->  \\\'\\\'"\n\n\
arrow6 = arrow5\n\n\
arrow7 = "->   \\r  "\n\n\
finaltest = " - outer-pre - \\" - inner - \\" - outer-pro - "\n')
        FILE_BUFFER.close()
    
    # Replaceable string for testing
    replacements['arrow'] = 'AR'


def PerformSubstitution(filename, unbiased=False):
    if unbiased:
        print('\nWARNING: Using unbiased scan (will not check for string literals)\n')
    
    F_relative = filename.replace('{}/'.format(root_dir), '')
    
    if TESTING:
        # Only perform testing on 'test.py' file in root directory
        if F_relative.rstrip('.py') != 'test':
            print('[TESTING] Skipping file: {}'.format(filename))
            
            return False
    
    FILE_BUFFER = open(filename, 'r')
    # TODO: Split the text into lines for accurate checking
    original_text = FILE_BUFFER.read()
    FILE_BUFFER.close()
    
    for OLD in replacements:
        if OLD in original_text:
            excludes = None
            NEW = replacements[OLD]
            
            if isinstance(NEW, (tuple, list)):
                excludes = None
                if len(NEW) > 1:
                    excludes = NEW[1]
                
                NEW = NEW[0]
            
            if excludes and os.path.basename(filename).rstrip('.py') in excludes:
                print('\n{}: Excluding file from replacement of text "{}"'.format(F_relative, OLD))
                
                continue
            
            # DEBUG LINE
            print('\nChecking for string "{}" in file: {}'.format(OLD, filename))
            
            changed_lines = original_text.split('\n')
            
            line_number = 0
            for LI in changed_lines:
                line_index = line_number
                line_number += 1
                
                if LI.strip() and OLD in LI:
                    # DEBUG LINE
                    print('Found line: {}'.format(LI.strip()))
                    
                    # Only searching string literals
                    substrings = re.findall(pattern1, LI) + re.findall(pattern2, LI)
                    
                    # DEBUG LINE
                    #lprint('Substrings: {}'.format(substrings), line_number)
                    
                    string_literal = unbiased
                    
                    if not string_literal:
                        for SS in substrings:
                            if OLD in SS:
                                string_literal = True
                                break
                    
                    # Source is not within a string literal
                    if not string_literal:
                        # DEBUG LINE
                        lprint('Source string ({}) not within a string literal'.format(OLD), line_number)
                        
                        continue
                    
                    # DEBUG START
                    #str_index = LI.index(OLD)
                    
                    #lprint('Source string ({}) found at line index {}'.format(OLD, str_index), line_number)
                    # DEBUG END
                    
                    changed_lines[line_index] = LI.replace(OLD, NEW)
            
            changed_lines = '\n'.join(changed_lines)
            
            if changed_lines != original_text:
                print('Writing changes to file ...')
                
                FILE_BUFFER = open(filename, 'w')
                FILE_BUFFER.write(changed_lines)
                FILE_BUFFER.close()
                
                return True
            
            print('Not found')
    
    return False


# Manually specify files with command line

args = sys.argv[1:]
if args:
    for FILE in args:
        if os.path.isfile(FILE):
            # Use unbiased scan for non-source files
            PerformSubstitution(FILE, unbiased=not FILE.endswith('.py'))
    
    sys.exit(0)


# Directories excluded from search (Debreate's root dir would be denoted by an empty string '')
exclude_dirs = (
    '.git',
    '.settings',
    'bitmaps',
    'data',
    'debian',
    'docs',
    'locale',
    'man',
    'nbproject',
    'scripts',
    'templates',
    )

root_files = []
root_dirs = []

for OBJECT in sorted(os.listdir(root_dir)):
    if os.path.isfile(OBJECT) and OBJECT.endswith('.py'):
        root_files.append(ConcatPaths(root_dir, OBJECT))
        
        continue
    
    if os.path.isdir(OBJECT) and OBJECT not in exclude_dirs:
        root_dirs.append(ConcatPaths(root_dir, OBJECT))

root_files = tuple(root_files)
root_dirs = tuple(root_dirs)

if root_files and root_dir not in exclude_dirs:
    for F in root_files:
        if os.path.isfile(F):
            PerformSubstitution(F)

if root_dirs:
    for D in root_dirs:
        for ROOT, DIRS, FILES in os.walk(D):
            for F in FILES:
                if F.endswith('.py'):
                    F = ConcatPaths(ROOT, F)
                    
                    if os.path.isfile(F):
                        PerformSubstitution(F)
