#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Formats HTML Doxygen files for customized view

# MIT licensing
# See: docs/LICENSE.txt


import os, re, sys

from scripts_globals import ConcatPaths
from scripts_globals import DIR_root


print('\nOptimizing & customizing Doxygen HTML docs for Python ...\n')

DIR_html = ConcatPaths((DIR_root, 'docs/doxygen/html'))

if not os.path.isdir(DIR_html):
    print('ERROR: Doxygen directory does not exist, exiting ...')
    
    sys.exit(1)


files_root = []
files_rest = []

# Set files lists
for ROOT, DIRS, FILES in os.walk(DIR_html):
    for HTML in FILES:
        if HTML.lower().endswith('.html') and '_TEST' not in HTML:
            HTML = ConcatPaths((ROOT, HTML))
            
            if ROOT == DIR_html:
                files_root.append(HTML)
            
            else:
                files_rest.append(HTML)


## Converts leftover markdown syntax to HTML
def FormatMarkdown():
    global DIR_html
    
    FILE_index = ConcatPaths((DIR_html, 'index.html'))
    
    if os.path.isfile(FILE_index):
        print('Formatting markdown ...')
        
        FILE_BUFFER = open(FILE_index, 'r')
        text = FILE_BUFFER.read()
        FILE_BUFFER.close()
        
        # Bold & italic text
        new_text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<b><i>\1</i></b>', text)
        new_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', new_text)
        new_text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', new_text)
        
        # Anchors
        lines = new_text.split('\n')
        for INDEX in range(len(lines)):
            LINE = lines[INDEX]
            
            if '<h3>' in LINE:
                name = LINE.strip(' \t><').replace('><', '').split('>')[-1].split('<')[0].lower().replace(' ', '-')
                
                LINE = LINE.replace('<h3>', '<h3 id="{}">'.format(name))
                if LINE != lines[INDEX]:
                    lines[INDEX] = LINE
        
        new_text = '\n'.join(lines)
        
        if new_text != text:
            FILE_BUFFER = open(FILE_index, 'w')
            FILE_BUFFER.write(new_text)
            FILE_BUFFER.close()
            
            return True
    
    else:
        print('ERROR: Index file not found: {}'.format(FILE_index))
    
    return False


def FormatMethods():
    global files_root
    
    delims_remove = (
        'def&#160;',
        'class &#160;',
        )
    
    self_replacements = {
        '(self)': '( )',
        'self, ': '',
        }
    
    for HTML in files_root:
        FILE_BUFFER = open(HTML, 'r')
        text = FILE_BUFFER.read()
        FILE_BUFFER.close()
        
        # Find the module's & class's names
        module = None
        class_name = None
        if '<div class="title">' in text:
            module = text.split('<div class="title">')[1].split('\n')[0].split(' ')
            
            if module[1].lower() in ('class', 'member',):
                class_name = module[0].split('.')[-1]
            
            if module[1].lower() == 'namespace':
                module = module[0]
            
            else:
                module = '.'.join(module[0].split('.')[:-1])
            
            module += '.'
        
        new_text = None
        remove_indexes = []
        
        lines = text.split('\n')
        params = False
        for INDEX in range(len(lines)):
            LINE = lines[INDEX]
            
            if LINE.strip() == '<div class="memproto">':
                # Entered class method
                params = True
            
            elif params and '</div>' in LINE:
                # Exited class method
                params = False
            
            # Remove 'def' & 'class' declarations
            for DEF in delims_remove:
                if DEF in LINE:
                    LINE = LINE.replace(DEF, '')
            
            # Remove 'self' arguments
            if 'class="el"' in LINE:
                for SELF in self_replacements:
                    if SELF in LINE:
                        LINE = LINE.replace(SELF, self_replacements[SELF])
                
                if ' (' in LINE:
                    LINE = LINE.replace(' (', '(')
                
                if class_name and '__init__' in LINE:
                    LINE = LINE.replace('__init__', class_name)
            
            elif 'class="paramname"><em>self</em>' in LINE:
                if ')' in LINE:
                    LINE = LINE.replace('<td class="paramname"><em>self</em></td>', '')
                
                else:
                    if 'class="paramtype">' in lines[INDEX-1]:
                        remove_indexes.append(INDEX-1)
                    
                    remove_indexes.append(INDEX)
            
            elif LINE.strip() == '<td class="paramtype">&#160;</td>':
                remove_indexes.append(INDEX)
            
            elif 'class="paramname"' in LINE:
                if '&#160;' in LINE:
                    LINE = LINE.replace('&#160;', '')
                
                if ' = ' in LINE:
                    LINE = LINE.replace(' = ', '=')
                
                if lines[INDEX-1].strip() == '<td></td>':
                    remove_indexes.append(INDEX-1)
                
                if lines[INDEX+1].strip() == '<td></td>':
                    remove_indexes.append(INDEX+1)
            
            elif 'class="memname"' in LINE:
                if 'def ' in LINE:
                    LINE = LINE.replace('def ', '')
                
                if '.__init__ ' in LINE:
                    LINE = LINE.replace('.__init__ ', '')
                
                if module in LINE:
                    LINE = LINE.replace(module, '')
            
            elif params:
                # Entered class method
                if LINE.strip() == '</tr>':
                    # Do not split parameters by newline
                    if not INDEX + 1 > len(lines) and lines[INDEX+1].strip() == '<tr>':
                        remove_indexes += [INDEX, INDEX+1]
                
                elif 'class="memname"' in LINE:
                    if ' </td>' in LINE:
                        LINE = LINE.replace(' </td>', '(</td>')
                        
                        if lines[INDEX+1].strip() == '<td>(</td>':
                            remove_indexes.append(INDEX+1)
            
            if LINE != lines[INDEX]:
                lines[INDEX] = LINE
        
        for INDEX in reversed(remove_indexes):
            lines.pop(INDEX)
        
        new_text = '\n'.join(lines)
        
        if new_text and new_text != text:
            FILE_BUFFER = open(HTML, 'w')
            FILE_BUFFER.write(new_text)
            FILE_BUFFER.close()


FormatMarkdown()
FormatMethods()
