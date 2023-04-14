
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module globals.dateinfo

from datetime import datetime
from time     import strftime

from globals.strings import GS
from libdbr.logger   import Logger


__logger = Logger(__name__)

## Formatting methods for dates & times
#
#  Formats:
#  DEFAULT (none), CL (changelog), LOG (logger)
class dtfmt:
  DEFAULT = 0
  CL = 1
  LOG = 2
  STAMP = 3


## Prepends a zero to single-digit numbers
#
#  \return
#  \b \e String representation of digit
def _digit_to_string(number):
  __logger.deprecated(_digit_to_string, alt="libdbr.dateinfo.digitToString")

  if number < 10:
    return GS("0{}".format(number))

  return GS(number)


## Retrieves the current year
#
#  FIXME: Should return value default to integer?
#  \return
#  \b \e String representation of the current year
def GetYear(fmt=dtfmt.DEFAULT, string_value=True):
  __logger.deprecated(GetYear, alt="libdbr.dateinfo.getYear")

  year = GS(strftime("%Y"))

  if not string_value:
    year = int(year)

  return year


## TODO: Doxygen
def GetMonthInt(string_value=False):
  __logger.deprecated(GetMonthInt, alt="libdbr.dateinfo.getMonth")

  month = GS(strftime("%m"))

  if not string_value:
    month = int(month)

  return month


## TODO: Doxygen
def GetDayInt(string_value=False):
  __logger.deprecated(GetDayInt, alt="libdbr.dateinfo.getDay")

  day = GS(strftime("%d"))

  if not string_value:
    day = int(day)

  return day


## Retrieves today's date
#
#  \param changelog
#  If \b \e True, formats output to Debian changelog standard
#  \return
#  \b \e String representation of date
def GetDate(fmt=dtfmt.DEFAULT):
  __logger.deprecated(GetDate, alt="libdbr.dateinfo.getDate")

  yr = GetYear()

  if fmt == dtfmt.CL:
    # Format: Wkdy, DD Mon YYYY
    # NOTE: May be a simpler method
    return "{} {}".format(strftime("%a, %d %b"), yr)

  if fmt == dtfmt.STAMP:
    # YYYYMMDD_HHMMSSmmm
    return "{}_{}".format(strftime("%Y%m%d"), GetTime(fmt))

  # Format: YYYY-MM-DD
  return "{}-{}".format(yr, strftime("%m-%d"))


## Retrieves current time
def GetTime(fmt=dtfmt.DEFAULT):
  __logger.deprecated(GetTime, alt="libdbr.dateinfo.getTime")

  ms = None
  current_time = None

  if fmt in (dtfmt.LOG, dtfmt.STAMP,):
    ms = GS(datetime.now().strftime("%f"))[:3]

    if fmt == dtfmt.STAMP:
      # HHMMSSmmm
      current_time = "{}{}".format(GS(strftime("%H%M%S")), ms)

    else:
      # HH:MM:SS.mmm
      current_time = "{}.{}".format(GS(strftime("%T")), ms)

  return current_time


## Retrieves current time zone
def GetTimeZone(fmt=dtfmt.DEFAULT):
  __logger.deprecated(GetTimeZone, alt="libdbr.dateinfo.getTimeZone")

  return GS(strftime("%z"))
