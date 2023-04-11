
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

import os

from wx import Dialog
from wx import GenericDirCtrl
from wx import App

from libdbr          import paths
from libdbr.logger   import Logger
from libdbr.unittest import assertEquals
from libdbr.unittest import assertNotNone
from libdbr.unittest import assertTrue


__logger = Logger(__name__)

def init():
  app = App()
  import ui.tree

  dialog = Dialog(None)
  app.SetTopWindow(dialog)

  user_home = paths.getUserHome(strict=True)

  __logger.debug("testing standard wx tree element ...")

  tree = GenericDirCtrl(dialog, dir=user_home)
  assertNotNone(tree)
  assertTrue(isinstance(tree, GenericDirCtrl))
  __logger.debug("starting path: {}".format(tree.GetPath()))
  assertTrue(os.path.isdir(tree.GetPath()))
  assertEquals(user_home, tree.GetPath())
  # ~ dialog.ShowModal()
  tree.Destroy()

  __logger.debug("testing custom directory tree element ...")

  panel = ui.tree.DirectoryTreePanel(dialog)
  assertNotNone(panel)
  assertTrue(isinstance(panel, ui.tree.DirectoryTreePanel))
  tree = ui.tree.DirectoryTree(panel)
  assertNotNone(tree)
  assertTrue(isinstance(tree, ui.tree.DirectoryTree))
  panel.setTree(tree)
  assertEquals(tree, panel.getTree())
  __logger.debug("starting path: {}".format(tree.GetPath()))
  assertTrue(os.path.isdir(tree.GetPath()))
  assertEquals(user_home, tree.GetPath())
  # ~ dialog.ShowModal()
  panel.Destroy()

  dialog.Destroy()
  app.MainLoop()
