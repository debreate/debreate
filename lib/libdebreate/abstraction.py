
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

from libdbr.logger import Logger


_logger = Logger(__name__)

## Error thrown when an inheriting class does not override an abstract method.
class MemberOverrideError(TypeError):
  def __init__(self, base, member, child):
    super().__init__("'{}' does not override '{}'"
        .format(child.__module__ + "." + child.__class__.__name__,
            base.__module__ + "." + base.__name__ + "." + member.__name__))

## Super interface for abstract classes.
class AbstractClass:
  def __init__(self, super_class):
    for member in dir(self):
      try:
        member = getattr(self, member)
        if hasattr(member, "__isabstractmethod__") and member.__isabstractmethod__:
          raise MemberOverrideError(super_class, member, self)
      except RuntimeError:
        # ignore uninitialized
        _logger.debug("skipping uninitialized member check '{}.{}.{}'".format(self.__module__,
            self.__class__.__name__, member))
