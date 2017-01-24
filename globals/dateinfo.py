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
class dtfmt:
    DEFAULT = 0
    CL = 1
    LOG = 2
    STAMP = 3


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
def GetYear(fmt=dtfmt.DEFAULT, string_value=True):
    year = GS(strftime(u'%Y'))
    
    if not string_value:
        year = int(year)
    
    return year


## TODO: Doxygen
def GetMonthInt(string_value=False):
    month = GS(strftime(u'%m'))
    
    if not string_value:
        month = int(month)
    
    return month


## TODO: Doxygen
def GetDayInt(string_value=False):
    day = GS(strftime(u'%d'))
    
    if not string_value:
        day = int(day)
    
    return day


## Retrieves today's date
#  
#  \param changelog
#    If \b \e True, formats output to Debian changelog standard
#  \return
#    \b \e String representation of date
def GetDate(fmt=dtfmt.DEFAULT):
    yr = GetYear()
    
    if fmt == dtfmt.CL:
        # Format: Wkdy, DD Mon YYYY
        # NOTE: May be a simpler method
        return u'{} {}'.format(strftime(u'%a, %d %b'), yr)
    
    if fmt == dtfmt.STAMP:
        # YYYYMMDD_HHMMSSmmm
        return u'{}_{}'.format(strftime(u'%Y%m%d'), GetTime(fmt))
    
    # Format: YYYY-MM-DD
    return u'{}-{}'.format(yr, strftime(u'%m-%d'))


## Retrieves current time
def GetTime(fmt=dtfmt.DEFAULT):
    ms = None
    current_time = None
    
    if fmt in (dtfmt.LOG, dtfmt.STAMP,):
        ms = GS(datetime.now().strftime(u'%f'))[:3]
        
        if fmt == dtfmt.STAMP:
            # HHMMSSmmm
            current_time = u'{}{}'.format(unicode(strftime(u'%H%M%S')), ms)
        
        else:
            # HH:MM:SS.mmm
            current_time = u'{}.{}'.format(unicode(strftime(u'%T')), ms)
    
    return current_time


## Retrieves current time zone
def GetTimeZone(fmt=dtfmt.DEFAULT):
    return GS(strftime(u'%z'))
