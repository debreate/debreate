
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## Custom types.
#
#  @module libdbr.types


## Representation of a two-index tuple.
#
#  @param first
#    Object at first index.
#  @param second
#    Object at second index.
class Pair:
  def __init__(self, first, second):
    f_type = type(first); s_type = type(second)
    if f_type != s_type:
      raise TypeError("'{}' attributes must be of the same type, found '({}, {})'"
          .format(Pair.__name__, f_type.__name__, s_type.__name__))
    self.__first = first; self.__second = second

  ## Converts object to be compatible with `tuple` types.
  def __tuple(self):
    return (self.__first, self.__second)

  ## Throws a comparison error.
  #
  #  @param _type
  #    Type causing error.
  #  @param oper
  #    Operator in question.
  def __compare_error(self, _type, oper):
    raise TypeError("'{}' cannot be compared to '{}' using operator '{}'"
        .format(_type.__name__, Pair.__name__, oper))

  def __eq__(self, other):
    o_type = type(other)
    if o_type in (Pair, list, tuple):
      return tuple(other) == tuple(self)
    return False

  def __ne__(self, other):
    o_type = type(other)
    if o_type in (Pair, list, tuple):
      return tuple(other) != tuple(self)
    return True

  def __gt__(self, other):
    o_type = type(other)
    if o_type in (Pair, list, tuple):
      return tuple(other) > tuple(tuple)
    self.__compare_error(o_type, ">")

  def __ge__(self, other):
    o_type = type(other)
    if o_type in (Pair, list, tuple):
      return tuple(other) >= tuple(self)
    self.__compare_error(o_type, ">=")

  def __lt__(self, other):
    o_type = type(other)
    if o_type in (Pair, list, tuple):
      return tuple(other) < tuple(self)
    self.__compare_error(o_type, "<")

  def __le__(self, other):
    o_type = type(other)
    if o_type in (Pair, list, tuple):
      return tuple(other) <= tuple(self)
    self.__compare_error(o_type, "<=")

  def __str__(self):
    return str(self.__tuple())

  def __getitem__(self, idx):
    return self.__tuple()[idx]

  ## Converts first & second attributes into string.
  #
  #  @param sep
  #    String separating first & second attributes.
  #  @return
  #    String representation.
  def join(self, sep):
    return "{}{}{}".format(self.__first, sep, self.__second)

  ## Retrieves first attribute.
  def first(self):
    return self.__first

  ## Retrieves second attribute.
  def second(self):
    return self.__second
