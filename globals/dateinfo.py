# -*- coding: utf-8 -*-

## \package globals.dateinfo

# MIT licensing
# See: docs/LICENSE.txt


from datetime   import datetime
from time       import strftime

from globals.strings import GS


## Formatting methods for dates & times
#  
#  Formats:
#    DEFAULT (none), CL (changelog), LOG (logger)
class DTFMT:
    DEFAULT = 0
    CL = 1
    LOG = 2


## Prepends a zero to single-digit numbers
#  
#  \return
#    \b \e String representation of digit
def _digit_to_string(number):
    if number < 10:
        return unicode(u'0{}'.format(number))
    
    return GS(number)


## Retrieves the current year
#  
#  FIXME: Should return value default to integer?
#  \return
#    \b \e String representation of the current year
def GetYear(fmt=DTFMT.DEFAULT, string_value=True):
    year = GS(strftime(u'%Y'))
    
    if not string_value:
        year = int(year)
    
    return year


## Retrieves today's date
#  
#  \param changelog
#    If \b \e True, formats output to Debian changelog standard
#  \return
#    \b \e String representation of date
def GetDate(fmt=DTFMT.DEFAULT):
    yr = GetYear()
    
    if fmt == DTFMT.CL:
        # Format: Wkdy, DD Mon YYYY
        # NOTE: May be a simpler method
        return u'{} {}'.format(strftime(u'%a, %d %b'), yr)
    
    # Format: YYYY-MM-DD
    return u'{}-{}'.format(yr, strftime(u'%m-%d'))


## Retrieves current time
def GetTime(fmt=DTFMT.DEFAULT):
    ms = None
    
    if fmt in (DTFMT.LOG,):
        ms = GS(datetime.now().strftime(u'%f'))[:3]
    
    current_time = unicode(strftime(u'%T'))
    
    if ms != None:
        current_time = u'{}.{}'.format(current_time, ms)
    
    return current_time


## Retrieves current time zone
def GetTimeZone(fmt=DTFMT.DEFAULT):
    return GS(strftime(u'%z'))
