
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

  ## Directives for resetting page to default values.
  @abstractmethod
  def reset(self):
    pass
