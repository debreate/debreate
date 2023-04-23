
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

from abc import abstractmethod

from .                       import panel
from libdbr.logger           import Logger
from libdebreate             import ident
from libdebreate.abstraction import AbstractClass


_logger = Logger(__name__)

## Abstract class for wizard pages.
class Page(panel.ScrolledPanel, AbstractClass):

  def __init__(self, parent, id=-1):
    panel.ScrolledPanel.__init__(self, parent, id)
    AbstractClass.__init__(self, Page)

    self.__error_code = 0
    self.__error_message = None

    self.__label = ""
    if id in ident.pgid.Labels:
      self.__label = ident.pgid.Labels[id]

  ## Directives when page is added to wizard.
  @abstractmethod
  def init(self):
    pass

  ## Alias of `ui.page.Page.init` for backward compatibility.
  def InitPage(self):
    self.init()

  ## Implementing classes should return data to be exported to file & used for build process.
  #
  #  @return
  #    Page data.
  @abstractmethod
  def toString(self):
    pass

  ## Alias of `ui.page.Page.toString` for backward compatibility.
  def Get(self):
    return self.toString()

  ## Alias of `ui.page.Page.toString` for backward compatibility.
  def GetSaveData(self):
    return self.toString()

  ## Retrieves label to display at page top.
  #
  #  @return
  #    String label.
  def getLabel(self):
    return self.__label

  ## Alias of `ui.page.Page.getLabel` for backward compatibility.
  def GetLabel(self):
    return self.getLabel()

  ## Alias of `ui.page.Page.getLabel` for backward compatibility.
  def GetName(self):
    return self.getLabel()

  ## Sets error info.
  #
  #  @param code
  #    Error code.
  #  @param msg
  #    Text to use for error.
  def setError(self, code, msg):
    self.__error_code = int(code)
    self.__error_message = str(msg)

  ## Retrievies the most recent error information.
  #
  #  @return
  #    Error code & message.
  def getError(self):
    code = self.__error_code
    msg = self.__error_message
    # reset for sequential result
    self.__error_code = 0
    self.__error_message = None
    return code, msg

  ## Directives for loading data from file.
  #
  #  @param filepath
  #    Path to file to be loaded.
  #  @return
  #    Error code.
  def importFile(self, filepath):
    _logger.error("'{}' does not override '{}'".format(
        self.__module__ + "." + self.__class__.__name__,
        Page.__module__ + "." + Page.__name__ + "." + Page.importFile.__name__))
    return 0

  ## Alias of `ui.page.Page.importFile` for backward compatibility.
  def ImportFromFile(self, filepath):
    return self.importFile(filepath)

  ## Backwards compatibility.
  def Export(self):
    msg = "'{}' does not override '{}'".format(
        self.__module__ + "." + self.__class__.__name__,
        Page.__module__ + "." + Page.__name__ + "." + Page.Export.__name__)
    _logger.error(msg)
    raise TypeError(msg)

  ## Directives for resetting page to default values.
  @abstractmethod
  def reset(self):
    pass

  ## Alias of `ui.page.Page.reset` for backward compatibility.
  def Reset(self):
    self.reset()

  ## Inheriting classes should override for sanity checks & setting error message.
  def isOkay(self):
    _logger.warn("'{}' does not override '{}'".format(
        self.__module__ + "." + self.__class__.__name__,
        Page.__module__ + "." + Page.__name__ + "." + Page.isOkay.__name__))
    return True

  ## Alias of `ui.page.Page.isOkay` for backward compatibility
  def IsOkay(self):
    return self.isOkay()
