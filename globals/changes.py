# -*- coding: utf-8 -*-

## \package globals.changes

# MIT licensing
# See: docs/LICENSE.txt


from globals.application    import APP_name
from globals.application    import AUTHOR_email
from globals.application    import AUTHOR_name
from globals.application    import VERSION_string
from globals.dateinfo       import DTFMT
from globals.dateinfo       import GetDate
from globals.dateinfo       import GetTime
from globals.dateinfo       import GetTimeZone
from globals.strings        import RemoveEmptyLines
from globals.strings        import TextIsEmpty
from globals.system         import OS_codename


section_delims = u'*-+#'

def _strip_line(line, chars, preserve_indent=False):
    if preserve_indent:
        return line.rstrip(chars)
    
    return line.strip(chars)


## Formats lines for changelog output
def _format_lines(lines, preserve_indent=False):
    if isinstance(lines, tuple):
        lines = list(lines)
    
    if lines:
        global section_delims
        
        for INDEX in range(len(lines)):
            # Clean leading & trailing whitespace
            lines[INDEX] = _strip_line(lines[INDEX], u' \t', preserve_indent)
            
            if INDEX == 0:
                # First line will always start with an asterix
                # FIXME: Indentation not saved here
                lines[INDEX] = u'  * {}'.format(lines[INDEX].lstrip(u' {}'.format(section_delims)))
                continue
            
            section = False
            
            # Make sure line is not empty before setting section
            if lines[INDEX] and lines[INDEX][0] in section_delims:
                section = True
                lines[INDEX] = lines[INDEX][1:].strip()
            
            if section:
                lines[INDEX] = u'  * {}'.format(lines[INDEX])
            
            else:
                lines[INDEX] = u'    {}'.format(lines[INDEX])
    
    return tuple(lines)


## Formats date & time for changelog
def _get_cl_timestamp():
    fmt = DTFMT.CL
    return u'{} {} {}'.format(GetDate(fmt), GetTime(fmt), GetTimeZone(fmt))


## Function to format text Debian changelog standards
#  
#  \param text
#    \b \e String to be formatted
#  \return
#    Debian changelog format
def FormatChangelog(text, name=APP_name, version=VERSION_string, dist=OS_codename,
            urgency=u'low', packager=AUTHOR_name, email=AUTHOR_email, preserve_indent=False):
    if TextIsEmpty(text):
        return None
    
    # Remove leading & trailing whitespace & empty lines & split into
    # list of lines.
    lines = text.strip(u' \t\n\r').split(u'\n')
    
    if not lines:
        return None
    
    lines = RemoveEmptyLines(lines)
    lines = _format_lines(lines, preserve_indent)
    
    text = u'\n'.join(lines)
    header = u'{} ({}) {}; urgency={}\n'.format(name, version, dist, urgency)
    footer = u'\n -- {} <{}>  {}'.format(packager, email, _get_cl_timestamp())
    
    return u'\n'.join((header, text, footer))
