## \page main.py Main Window Interface
#
#  Defines interface of the main window.

# MIT licensing
# See: docs/LICENSE.txt


import os, shutil, subprocess, urllib, webbrowser, wx, wx.html
from urllib.error import HTTPError
from urllib.error import URLError

from dbr.config				import GetDefaultConfigValue
from dbr.config				import WriteConfig
from dbr.event				import EVT_CHANGE_PAGE
from dbr.event				import EVT_TIMER_STOP
from dbr.functions			import GetCurrentVersion
from dbr.functions			import UsingDevelopmentVersion
from dbr.help				import HelpDialog
from dbr.icon				import Icon
from dbr.language			import GT
from dbr.log				import DebugEnabled
from dbr.log				import Logger
from dbr.timer				import DebreateTimer
from fileio.fileio			import ReadFile
from fileio.fileio			import WriteFile
from globals.application	import APP_homepage
from globals.application	import APP_project_gh
from globals.application	import APP_project_sf
from globals.application	import AUTHOR_email
from globals.application	import AUTHOR_name
from globals.application	import VERSION_string
from globals.application	import VERSION_tuple
from globals.bitmaps		import LOGO
from globals.execute		import GetExecutable
from globals.ident			import menuid
from globals.ident			import pgid
from globals.moduleaccess	import ModuleAccessCtrl
from globals.paths			import ConcatPaths
from globals.paths			import PATH_app
from globals.paths			import PATH_cache
from globals.paths			import PATH_local
from globals.project		import PROJECT_ext
from globals.project		import PROJECT_txt
from globals.strings		import GS
from globals.threads		import Thread
from startup.tests			import GetTestList
from ui.about				import AboutDialog
from ui.dialog				import ConfirmationDialog
from ui.dialog				import DetailedMessageDialog
from ui.dialog				import ShowErrorDialog
from ui.distcache			import DistNamesCacheDialog
from ui.layout				import BoxSizer
from ui.menu				import createMenuBar
from ui.progress			import ProgressDialog
from ui.quickbuild			import QuickBuild
from ui.statusbar			import StatusBar
from wiz.helper				import GetPage
from wiz.pginit				import Page as PageInit
from wiz.wizard				import Wizard


default_title = GT(u'Debreate - Debian Package Builder')


## The main window interface
class MainWindow(wx.Frame, ModuleAccessCtrl):
	## Constructor
	#
	#  \param pos
	#	<b><i>Integer tuple</i></b> or <b><i>wx.Point</i></b> instance indicating the screen position of the window
	#  \param size
	#	<b><i>Integer tuple</i></b> or <b><i>wx.Size</i></b> instance indicating the dimensions of the window
	def __init__(self, pos, size):
		wx.Frame.__init__(self, None, wx.ID_ANY, default_title, pos, size)
		ModuleAccessCtrl.__init__(self, __name__)

		self.timer = DebreateTimer(self)
		# placeholder for progress dialog
		self.progress = None

		self.Bind(wx.EVT_TIMER, self.__onTimerEvent)
		self.Bind(EVT_TIMER_STOP, self.__onTimerStop)

		# Make sure that this frame is set as the top window
		if not wx.GetApp().GetTopWindow() == self:
			Logger.Debug(__name__, GT(u'Setting MainWindow instance as top window'))

			wx.GetApp().SetTopWindow(self)

		if DebugEnabled():
			self.SetTitle(u'{} ({})'.format(default_title, GT(u'debugging')))

		self.SetMinSize(wx.Size(640, 400))

		# ----- Set Titlebar Icon
		self.SetIcon(Icon(LOGO))

		# *** Status Bar *** #
		StatusBar(self)

		# *** Menus *** #
		createMenuBar(self)

		self.Wizard = Wizard(self)

		# *** Current Project Status *** #

		self.LoadedProject = None
		self.ProjectDirty = False

		# *** Event Handling *** #

		wx.EVT_MENU(self, menuid.NEW, self.OnProjectNew)
		wx.EVT_MENU(self, menuid.OPEN, self.OnProjectOpen)
		wx.EVT_MENU(self, menuid.SAVE, self.OnProjectSave)
		wx.EVT_MENU(self, menuid.SAVEAS, self.OnProjectSave)
		wx.EVT_MENU(self, menuid.QBUILD, self.OnQuickBuild)
		wx.EVT_MENU(self, menuid.EXIT, self.OnQuit)

		wx.EVT_MENU(self, menuid.TOOLTIPS, self.OnToggleToolTips)
		wx.EVT_MENU(self, menuid.DIST, self.OnUpdateDistNamesCache)

		wx.EVT_MENU(self, menuid.UPDATE, self.OnCheckUpdate)
		wx.EVT_MENU(self, menuid.HELP, self.OnHelp)
		wx.EVT_MENU(self, menuid.ABOUT, self.OnAbout)

		self.Bind(EVT_CHANGE_PAGE, self.OnWizardBtnPage)

		# Custom close event shows a dialog box to confirm quit
		wx.EVT_CLOSE(self, self.OnQuit)

		# *** Layout *** #

		lyt_main = BoxSizer(wx.VERTICAL)
		lyt_main.Add(self.Wizard, 1, wx.EXPAND)

		self.SetAutoLayout(True)
		self.SetSizer(lyt_main)
		self.Layout()


	## Retrieves menu by ID
	def GetMenu(self, menuId):
		return self.GetMenuBar().GetMenuById(menuId)


	## Retrieves the Wizard instance
	#
	#  \return
	#		wiz.wizard.Wizard
	def GetWizard(self):
		return self.Wizard


	## Sets the pages in the wiz.wizard.Wizard instance
	def InitWizard(self):
		self.Wizard.AddPage(PageInit(self.Wizard))
		self.Wizard.SetModeBin(0)


	## TODO: Doxygen
	def IsNewProject(self):
		title = self.GetTitle()
		if title == default_title:
			return True

		else:
			return False


	## TODO: Doxygen
	def IsSaved(self):
		title = self.GetTitle()
		if title[-1] == u'*':
			return False

		else:
			return True


	## Opens a dialog box with information about the program
	def OnAbout(self, event=None): #@UnusedVariable
		about = AboutDialog(self)

		about.SetGraphic(LOGO)
		about.SetVersion(VERSION_string)
		about.SetDescription(GT(u'A package builder for Debian based systems'))
		about.SetAuthor(AUTHOR_name)

		about.SetWebsites((
			(GT(u'Homepage'), APP_homepage),
			(GT(u'GitHub Project'), APP_project_gh),
			(GT(u'Sourceforge Project'), APP_project_sf),
		))

		about.AddJobs(
			AUTHOR_name,
			(
				GT(u'Head Developer'),
				GT(u'Packager'),
				u'{} (es, it)'.format(GT(u'Translation')),
			),
			AUTHOR_email
		)

		about.AddJobs(
			u'Hugo Posnic',
			(
				GT(u'Code Contributor'),
				GT(u'Website Designer & Author'),
			),
			u'hugo.posnic@gmail.com'
		)

		about.AddJob(u'Lander Usategui San Juan', GT(u'General Contributor'), u'lander@erlerobotics.com')

		about.AddTranslator(u'Karim Oulad Chalha', u'herr.linux88@gmail.com', u'ar', )
		about.AddTranslator(u'Philippe Dalet', u'philippe.dalet@ac-toulouse.fr', u'fr')
		about.AddTranslator(u'Zhmurkov Sergey', u'zhmsv@yandex.ru', u'ru')

		about.AddJob(u'Benji Park', GT(u'Button Base Image Designer'))

		about.SetChangelog()

		about.SetLicense()

		about.ShowModal()
		about.Destroy()


	## Checks for new release availability
	def OnCheckUpdate(self, event=None): #@UnusedVariable
		update_test = u'update-fail' in GetTestList()

		if UsingDevelopmentVersion() and not update_test:
			DetailedMessageDialog(self, GT(u'Update'),
					text=GT(u'Update checking is disabled in development versions')).ShowModal()
			return

		wx.SafeYield()

		if update_test:
			# Set a bad url to force error
			current = GetCurrentVersion(u'http://dummyurl.blah/')

		else:
			current = GetCurrentVersion()

		Logger.Debug(__name__, GT(u'URL request result: {}').format(current))

		error_remote = GT(u'An error occurred attempting to contact remote website')

		if isinstance(current, (URLError, HTTPError)):
			current = GS(current)
			ShowErrorDialog(error_remote, current)

		elif isinstance(current, tuple) and current > VERSION_tuple:
			current = u'{}.{}.{}'.format(current[0], current[1], current[2])
			l1 = GT(u'Version {} is available!').format(current)
			l2 = GT(u'Would you like to go to Debreate\'s website?')
			if ConfirmationDialog(self, GT(u'Update'), u'{}\n\n{}'.format(l1, l2)).Confirmed():
				wx.LaunchDefaultBrowser(APP_homepage)

		elif isinstance(current, str):
			ShowErrorDialog(error_remote, current)

		else:
			DetailedMessageDialog(self, GT(u'Debreate'), text=GT(u'Debreate is up to date!')).ShowModal()


	def __cacheManualFiles(self, args):
		url_manual = args[0]
		manual_cache = args[1]
		manual_index = args[2]
		main_dir = os.getcwd()
		os.chdir(manual_cache)

		try:
			subprocess.Popen([u'wget', u'-rkp', u'-nd', u'-np', u'-H', u'-D',
					u'debreate.wordpress.com,antumdeluge.github.io', url_manual]).communicate()
			# FIXME: use Python commands
			subprocess.Popen([u'sed', u'-i', u'-e', u's|<a.*>||g', u'-e', u's|</a>||g', manual_index]).communicate()
		except:
			# FIXME: show error message
			pass

		os.chdir(main_dir)
		self.timer.Stop()

	## Calls Pulse method on progress dialog when timer event occurs
	def __onTimerEvent(self, event=None):
		if self.progress:
			self.progress.Pulse()

	def __onTimerStop(self, event=None):
		if self.progress:
			self.progress.EndModal(0)
			self.progress = None

		if not self.IsEnabled():
			self.Enable()

		return not self.progress


	## Action to take when 'Help' is selected from the help menu
	#
	#  Opens a help dialog if using 'alpha' test. Otherwise, opens
	#  PDF usage document. If openening usage document fails, attempts
	#  to open web browser in remote usage page.
	#  TODO: Use dialog as main method
	def OnHelp(self, event=None): #@UnusedVariable
		if u'alpha' in GetTestList():
			HelpDialog(self).ShowModal()
		else:
			# FIXME: files should be re-cached when Debreate upgraded to new version
			# TODO: trim unneeded text
			cached = False
			manual_cache = ConcatPaths(PATH_cache, u'manual')
			manual_index = ConcatPaths(manual_cache, u'index.html')
			if not os.path.isdir(manual_cache):
				os.makedirs(manual_cache)
			elif os.path.isfile(manual_index):
				cached = True
			url_manual = u'https://debreate.wordpress.com/manual/'
			# NOTE: use urllib.request.urlopen for Python 3
			manual_data = urllib.urlopen(url_manual)
			url_state = manual_data.getcode()
			if url_state == 200:
				# cache files
				if not cached:
					self.progress = ProgressDialog(self, message=GT(u'Caching manual files'),
							style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE)
					self.Disable()
					self.timer.Start(100)
					Thread(self.__cacheManualFiles, (url_manual, manual_cache, manual_index,)).Start()
					self.progress.ShowModal()
				manual_dialog = wx.Dialog(self, title=u'Debreate Manual', size=(800,500), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
				manual = wx.html.HtmlWindow(manual_dialog)
				wx.Yield()
				if manual.LoadFile(manual_index):
					manual_dialog.CenterOnParent()
					manual_dialog.ShowModal()
				else:
					wx.Yield()
					webbrowser.open(url_manual)
				manual_dialog.Destroy()
			else:
				# open local document
				wx.Yield()
				subprocess.call([u'xdg-open', u'{}/docs/usage.pdf'.format(PATH_app)])


	## Opens the logs directory in the system's default file manager
	def OnLogDirOpen(self, event=None): #@UnusedVariable
		Logger.Debug(__name__, GT(u'Opening log directory ...'))

		subprocess.check_output([GetExecutable(u'xdg-open'), u'{}/logs'.format(PATH_local)], stderr=subprocess.STDOUT)


	## Changes wizard page from menu
	def OnMenuChangePage(self, event=None):
		if isinstance(event, int):
			page_id = event

		else:
			page_id = event.GetId()

		self.Wizard.ShowPage(page_id)


	## TODO: Doxygen
	def OnProjectNew(self, event=None): #@UnusedVariable
		self.ResetPages()


	## TODO: Doxygen
	def OnProjectOpen(self, event=None): #@UnusedVariable
		projects_filter = u'|*.{};*.{}'.format(PROJECT_ext, PROJECT_txt)
		d = GT(u'Debreate project files')

		dia = wx.FileDialog(self, GT(u'Open Debreate Project'), os.getcwd(), u'',
				u'{}{}'.format(d, projects_filter), wx.FD_CHANGE_DIR)
		if dia.ShowModal() != wx.ID_OK:
			return

		# Get the path and set the saved project
		project = dia.GetPath()

		filename = os.path.basename(project)

		if self.OpenProject(filename):
			# Only set project open in memory if loaded completely
			self.LoadedProject = project

		else:
			self.LoadedProject = None


	## TODO: Doxygen
	def OnProjectSave(self, event=None):
		event_id = event.GetId()

		def SaveIt(path):
				# Gather data from different pages
				data = (
					GetPage(pgid.CONTROL).GetSaveData(),
					GetPage(pgid.FILES).GetSaveData(),
					GetPage(pgid.SCRIPTS).GetSaveData(),
					GetPage(pgid.CHANGELOG).GetSaveData(),
					GetPage(pgid.COPYRIGHT).GetSaveData(),
					GetPage(pgid.MENU).GetSaveData(),
					GetPage(pgid.BUILD).GetSaveData(),
					)

				# Create a backup of the project
				overwrite = False
				if os.path.isfile(path):
					backup = u'{}.backup'.format(path)
					shutil.copy(path, backup)
					overwrite = True

				# This try statement can be removed when unicode support is enabled
				try:
					WriteFile(path, u'[DEBREATE-{}]\n{}'.format(VERSION_string, u'\n'.join(data)))

					if overwrite:
						os.remove(backup)

				except UnicodeEncodeError:
					detail1 = GT(u'Unfortunately Debreate does not support unicode yet.')
					detail2 = GT(u'Remove any non-ASCII characters from your project.')

					ShowErrorDialog(GT(u'Save failed'), u'{}\n{}'.format(detail1, detail2), title=GT(u'Unicode Error'))

					if overwrite:
						os.remove(path)
						# Restore project backup
						shutil.move(backup, path)

		def OnSaveAs():
			dbp = u'|*.dbp'
			d = GT(u'Debreate project files')
			dia = wx.FileDialog(self, GT(u'Save Debreate Project'), os.getcwd(), u'', u'{}{}'.format(d, dbp),
									wx.FD_SAVE|wx.FD_CHANGE_DIR|wx.FD_OVERWRITE_PROMPT)
			if dia.ShowModal() == wx.ID_OK:
				filename = dia.GetFilename()
				if filename.split(u'.')[-1] == u'dbp':
					filename = u'.'.join(filename.split(u'.')[:-1])

				self.LoadedProject = u'{}/{}.dbp'.format(os.path.split(dia.GetPath())[0], filename)

				SaveIt(self.LoadedProject)

		if event_id == wx.ID_SAVE:
			# Define what to do if save is pressed
			# If project already exists, don't show dialog
			if not self.IsSaved() or not self.LoadedProject or not os.path.isfile(self.LoadedProject):
				OnSaveAs()

			else:
				SaveIt(self.LoadedProject)

		else:
			# If save as is press, show the save dialog
			OnSaveAs()


	## TODO: Doxygen
	def OnQuickBuild(self, event=None): #@UnusedVariable
		QB = QuickBuild(self)
		QB.ShowModal()
		QB.Destroy()


	## Shows a dialog to confirm quit and write window settings to config file
	def OnQuit(self, event=None): #@UnusedVariable
		if ConfirmationDialog(self, GT(u'Quit?'),
				text=GT(u'You will lose any unsaved information')).ShowModal() in (wx.ID_OK, wx.OK):

			maximized = self.IsMaximized()
			WriteConfig(u'maximize', maximized)

			if maximized:
				WriteConfig(u'position', GetDefaultConfigValue(u'position'))
				WriteConfig(u'size', GetDefaultConfigValue(u'size'))
				WriteConfig(u'center', True)

			else:
				WriteConfig(u'position', self.GetPositionTuple())
				WriteConfig(u'size', self.GetSizeTuple())
				WriteConfig(u'center', False)

			WriteConfig(u'workingdir', os.getcwd())

			self.Destroy()


	## TODO: Doxygen
	def OnToggleTheme(self, event=None): #@UnusedVariable
		self.ToggleTheme(self)


	## Shows or hides tooltips
	def OnToggleToolTips(self, event=None): #@UnusedVariable
		enabled = self.opt_tooltips.IsChecked()
		wx.ToolTip.Enable(enabled)

		WriteConfig(u'tooltips', enabled)


	## Opens a dialog for creating/updating list of distribution names cache file
	def OnUpdateDistNamesCache(self, event=None): #@UnusedVariable
		DistNamesCacheDialog().ShowModal()


	## Updates the page menu to reflect current page
	def OnWizardBtnPage(self, event=None): #@UnusedVariable
		ID = self.Wizard.GetCurrentPageId()
		Logger.Debug(__name__, GT(u'Event: EVT_CHANGE_PAGE, Page ID: {}').format(ID))

		menu_page = self.GetMenu(menuid.PAGE)
		if not menu_page.IsChecked(ID):
			menu_page.Check(ID, True)


	## Deletes cache directory located at ~/.local/share/debreate/cache
	def OnClearCache(self, event=None):
		if os.path.isdir(PATH_cache):
			shutil.rmtree(PATH_cache)


	## Opens web links from the help menu
	def OpenPolicyManual(self, event=None):
		if isinstance(event, wx.CommandEvent):
			event_id = event.GetId()

		elif isinstance(event, int):
			event_id = event

		else:
			Logger.Error(__name__,
					u'Cannot open policy manual link with object type {}'.format(type(event)))

			return

		url = self.menu_policy.GetHelpString(event_id)
		webbrowser.open(url)


	## Retrieves filename of loaded project
	def ProjectGetLoaded(self):
		return self.LoadedProject


	## Tests project type & calls correct method to read project file
	#
	#  \param project_file
	#	\b \e unicode|str : Path to project file
	def OpenProject(self, project_file):
		Logger.Debug(__name__, u'Opening project: {}'.format(project_file))

		if not os.path.isfile(project_file):
			ShowErrorDialog(GT(u'Could not open project file'),
					GT(u'File does not exist or is not a regular file: {}').format(project_file))
			return False

		data = ReadFile(project_file)

		lines = data.split(u'\n')

		# FIXME: Need a better way to determine valid project
		app = lines[0].lstrip(u'[')
		if not app.startswith(u'DEBREATE'):
			ShowErrorDialog(GT(u'Could not open project file'),
					GT(u'Not a valid Debreate project: {}').format(project_file))
			return False

		if self.LoadedProject and not self.ResetPages():
			return False

		# *** Get Control Data *** #
		control_data = data.split(u'<<CTRL>>\n')[1].split(u'\n<</CTRL>>')[0]
		depends_data = self.Wizard.GetPage(pgid.CONTROL).Set(control_data)
		self.Wizard.GetPage(pgid.DEPENDS).Set(depends_data)

		# *** Get Files Data *** #
		files_data = data.split(u'<<FILES>>\n')[1].split(u'\n<</FILES>>')[0]
		opened = self.Wizard.GetPage(pgid.FILES).Set(files_data)

		# *** Get Scripts Data *** #
		scripts_data = data.split(u'<<SCRIPTS>>\n')[1].split(u'\n<</SCRIPTS>>')[0]
		self.Wizard.GetPage(pgid.SCRIPTS).Set(scripts_data)

		# *** Get Changelog Data *** #
		clog_data = data.split(u'<<CHANGELOG>>\n')[1].split(u'\n<</CHANGELOG>>')[0]
		self.Wizard.GetPage(pgid.CHANGELOG).Set(clog_data)

		# *** Get Copyright Data *** #
		try:
			cpright_data = data.split(u'<<COPYRIGHT>>\n')[1].split(u'\n<</COPYRIGHT')[0]
			self.Wizard.GetPage(pgid.COPYRIGHT).Set(cpright_data)

		except IndexError:
			pass

		# *** Get Menu Data *** #
		m_data = data.split(u'<<MENU>>\n')[1].split(u'\n<</MENU>>')[0]
		self.Wizard.GetPage(pgid.MENU).SetLauncherData(m_data, enabled=True)

		# Get Build Data
		build_data = data.split(u'<<BUILD>>\n')[1].split(u'\n<</BUILD')[0]#.split(u'\n')
		self.Wizard.GetPage(pgid.BUILD).Set(build_data)

		return opened


	## TODO: Doxygen
	def ProjectChanged(self, event=None):
		if DebugEnabled():
			Logger.Debug(__name__, u'MainWindow.OnProjectChanged:')
			print(u'  Object: {}'.format(event.GetEventObject()))

		self.ProjectDirty = True


	## TODO: Doxygen
	def ResetPages(self):
		warn_msg = GT(u'You will lose any unsaved information.')
		warn_msg = u'{}\n\n{}'.format(warn_msg, GT(u'Continue?'))

		if ConfirmationDialog(self, text=warn_msg).ShowModal() not in (wx.ID_OK, wx.OK):
			return False

		for page in self.Wizard.GetAllPages():
			page.Reset()

		self.SetTitle(default_title)

		# Reset the saved project field so we know that a project file doesn't exists
		self.LoadedProject = None

		return True


	## TODO: Doxygen
	def SetSavedStatus(self, status):
		if status: # If status is changing to unsaved this is True
			title = self.GetTitle()
			if self.IsSaved() and title != default_title:
				self.SetTitle(u'{}*'.format(title))


	## TODO: Doxygen
	#
	#  TODO: Finish definition
	def ToggleTheme(self, window):
		for C in window.GetChildren():
			self.ToggleTheme(C)

		bg_color = window.GetBackgroundColour()
		fg_color = window.GetForegroundColour()

		window.SetBackgroundColour(fg_color)
		window.SetForegroundColour(bg_color)
