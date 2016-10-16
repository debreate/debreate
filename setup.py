#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os, sys, errno


if len(sys.argv) > 1 and sys.argv[1].lower() == 'clean':
    print('Removing Makefile')
    
    if os.path.isfile('Makefile'):
        os.remove('Makefile')
    
    sys.exit(0)

required_files = (
    'Makefile.in',
    'INFO',
)

for F in required_files:
    if not os.path.isfile(F):
        print('ERROR: Required file does not exist: {}'.format(F))
        sys.exit(errno.ENOENT)


def StringIsEmpty(test_string):
    return ''.join(test_string.split(' ')) == ''


def GetKeyValue(target_file, key_name):
    if not os.path.isfile(target_file):
        print('ERROR: File does not exist: {}'.format(target_file))
        sys.exit(errno.ENOENT)
    
    FILE = open(target_file, 'r')
    lines = FILE.read().split('\n')
    FILE.close()
    
    ignore = (' ', '#')
    for L in lines:
        if len(L) and L[0] not in ignore and '=' in L:
            key = L.split('=')
            value = key[1].strip()
            key = key[0].strip()
            
            if StringIsEmpty(value):
                continue
            
            if key.lower() == key_name.lower():
                return value
    
    return


# *** Default settings *** #

default_prefix = '/usr/local'
default_icon_theme = '$(DATAROOT)/icons/gnome'.format(default_prefix)

build_definitions = {
    'prefix': default_prefix,
    #'package': GetKeyValue('INFO', 'NAME').lower(),
    'version': GetKeyValue('INFO', 'VERSION'),
    'icon-theme': default_icon_theme,
}

string_replacements = {
    '$(DATAROOT)': '<prefix>/share',
}


def SetVariable(key, default_value, value_type='path'):
    global build_definitions, string_replacements
    
    display_value = default_value
    
    for S in string_replacements:
        if S in display_value:
            display_value = display_value.replace(S, string_replacements[S])
    
    while True:
        print('Set {} ...'.format(key))
        input_var = raw_input('default [{}] : '.format(display_value))
        
        if input_var in ('exit', 'quit', 'abort'):
            print('Aborting ...')
            sys.exit(0)
        
        if not input_var:
            # Default value is used
            break
        
        elif not input_var.strip():
            print('ERROR: Value cannot be empty')
            continue
        
        if value_type == 'path' and input_var[0] not in ('/', '$',):
            print('ERROR: Invalid path: {}'.format(input_var))
            continue
        
        build_definitions[key] = input_var
        break

# *** User defined setup *** #

use_defaults = False
if len(sys.argv) > 1 and sys.argv[1].lower() == 'defaults':
    use_defaults = True


if not use_defaults:
    unfinished = True
    while unfinished:
        
        SetVariable('prefix', default_prefix)
        SetVariable('icon-theme', default_icon_theme)
        
        '''
        while True:
            print('\nSet prefix ...')
            input_prefix = raw_input('(default: [{}]) : '.format(default_prefix)).strip()
            
            if not input_prefix:
                input_prefix = default_prefix
            
            if input_prefix in ('exit', 'quit', 'abort'):
                print('Aborting ...')
                sys.exit(0)
            
            if StringIsEmpty(input_prefix) or input_prefix[0] != '/':
                print('Invalid prefix path: "{}"'.format(input_prefix))
                
                continue
            
            build_definitions['prefix'] = input_prefix
            break
        
        while True:
            print('\nSet icon theme path ...')
            input_icon_theme = raw_input('default [{}] : '.format(default_icon_theme))
        '''
        
        while True:
            print('\nPlease check the following build settings:')
            for D in build_definitions:
                display_definition = build_definitions[D]
                for S in string_replacements:
                    if S in display_definition:
                        display_definition = display_definition.replace(S, string_replacements[S])
                
                print('\t{}: {}'.format(D, display_definition))
            
            correct = raw_input('\nIs this correct [YES|no] : ').strip()
            
            if correct.lower() in ('y', 'yes') or not correct:
                unfinished = False
                break
            
            if correct.lower() in ('n', 'no'):
                break


# *** Creating the Makefile *** #

makefile_name = 'Makefile'
print('\nCreating {}...'.format(makefile_name))

if os.path.isfile(makefile_name):
    os.remove(makefile_name)

FILE = open('Makefile.in', 'r')
makefile_lines = FILE.read().split('\n')
FILE.close()

# Remove comments & lines at beginning of file
rm_lines = 0
for L in makefile_lines:
    if not L.strip():
        pass
    
    elif L[0] != '#':
        break
    
    rm_lines += 1
makefile_lines = makefile_lines[rm_lines:]

# Format new Makefile
'''
for L in makefile_lines:
    l_index = makefile_lines.index(L)
    for key in build_definitions:
        delim = '<{}>'.format(key)
        if delim in L:
            makefile_lines[l_index] = L.replace(delim, build_definitions[key])
'''

for key in build_definitions:
    for L in makefile_lines:
        l_index = makefile_lines.index(L)
        delim = '<{}>'.format(key)
        
        if delim in L:
            makefile_lines[l_index] = L.replace(delim, build_definitions[key])
            
            # Only replace first occurrence
            break

makefile_lines.insert(0, '# This file was generated by "{}"\n'.format(os.path.basename(__file__)))

FILE = open(makefile_name, 'w')
FILE.write('\n'.join(makefile_lines))
FILE.close()

sys.exit(0)
