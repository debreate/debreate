
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## Date & time formatting.
#
#  @module libdbr.dateinfo

from datetime import datetime
from time     import strftime


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
#  TODO: use use standard Python methods to pad with zeros
#
#  @param number
#    Integer to be modified.
#  @return
#    String representation of digit.
def digitToString(number):
  if number < 10:
    return "0{}".format(number)
  return str(number)

## Retrieves the current year.
#
#  @param fmt
#    dtfmt to use.
#  @param tostring
#    If true, convert returned value to string.
#  @return
#    Integer or string representation of year.
def getYear(fmt=dtfmt.DEFAULT, tostring=True):
  year = strftime("%Y")
  if not tostring:
    year = int(year)
  return year

## Retrieves the current month.
#
#  @param tostring
#    If true, convert returned value to string.
#  @return
#    Integer or string representation of month.
def getMonth(tostring=True):
  month = strftime("%m")
  if not tostring:
    month = int(month)
  return month

## Retrieves the current day of the month.
#
#  @param tostring
#    If true, convert returned value to string.
#  @return
#    Integer or string representation of day.
def getDay(tostring=True):
  day = strftime("%d")
  if not tostring:
    day = int(day)
  return day

## Retrieves today's date.
#
#  @param fmt
#    dtfmt to use.
#  @return
#    String representation of date.
def getDate(fmt=dtfmt.DEFAULT):
  yr = getYear()
  if fmt == dtfmt.CL:
    # format: Wkdy, DD Mon YYYY
    return "{} {}".format(strftime("%a, %d %b"), yr)
  if fmt == dtfmt.STAMP:
    # format YYYYMMDD_HHMMSSmmm
    return "{}_{}".format(strftime("%Y%m%d"), getTime(fmt))
  # format: YYYY-MM-DD
  return "{}-{}".format(yr, strftime("%m-%d"))

## Retrieves current time.
#
#  @param fmt
#    dtfmt to use.
#  @return
#    String representation of time.
def getTime(fmt=dtfmt.DEFAULT):
  ms = None
  current_time = None
  if fmt in (dtfmt.LOG, dtfmt.STAMP,):
    ms = datetime.now().strftime("%f")[:3]
    if fmt == dtfmt.STAMP:
      # format: HHMMSSmmm
      current_time = "{}{}".format(strftime("%H%M%S"), ms)
    else:
      # format: HH:MM:SS.mmm
      current_time = "{}.{}".format(strftime("%T"), ms)
  else:
    # format: HH:MM:SS
    current_time = strftime("%H:%M:%S")
  return current_time

## Retrieves current time zone.
#
#  @param fmt
#    dtfmt to use.
#  @return
#    String representation of timezone.
def getTimeZone(fmt=dtfmt.DEFAULT):
  return strftime("%z")

## Retrievies a date string formatted for Debian changelog.
def getDebianizedDate():
  return "{} {} {}".format(getDate(dtfmt.CL), getTime(dtfmt.CL), getTimeZone(dtfmt.CL))
