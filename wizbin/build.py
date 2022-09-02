## \package wizbin.build

# MIT licensing
# See: docs/LICENSE.txt


import os, shutil, subprocess, traceback, wx

from dbr.functions      import FileUnstripped
from dbr.language       import GT
from dbr.log            import DebugEnabled
from dbr.log            import Logger
from dbr.md5            import WriteMD5
from fileio.fileio      import ReadFile
from fileio.fileio      import WriteFile
from globals.bitmaps    import ICON_EXCLAMATION
from globals.bitmaps    import ICON_INFORMATION
from globals.errorcodes import dbrerrno
from globals.execute    import ExecuteCommand
from globals.execute    import GetExecutable
from globals.execute    import GetSystemInstaller
from globals.ident      import btnid
from globals.ident      import chkid
from globals.ident      import inputid
from globals.ident      import pgid
from globals.paths      import ConcatPaths
from globals.paths      import PATH_app
from globals.strings    import GS
from globals.strings    import RemoveEmptyLines
from globals.strings    import TextIsEmpty
from globals.system     import PY_VER_MAJ
from globals.tooltips   import SetPageToolTips
from input.toggle       import CheckBox
from input.toggle       import CheckBoxESS
from startup.tests      import UsingTest
from ui.button          import CreateButton
from ui.checklist       import CheckListDialog
from ui.dialog          import DetailedMessageDialog
from ui.dialog          import ShowErrorDialog
from ui.layout          import BoxSizer
from ui.output          import OutputLog
from ui.panel           import BorderedPanel
from ui.progress        import PD_DEFAULT_STYLE
from ui.progress        import ProgressDialog
from ui.progress        import TimedProgressDialog
from ui.style           import layout as lyt
from wiz.helper         import FieldEnabled
from wiz.helper         import GetField
from wiz.helper         import GetMainWindow
from wiz.helper         import GetPage
from wiz.wizard         import WizardPage


## Build page
class Page(WizardPage):
	## Constructor
	#
	#  \param parent
	#	Parent <b><i>wx.Window</i></b> instance
	def __init__(self, parent):
		WizardPage.__init__(self, parent, pgid.BUILD)

		# ----- Extra Options

		pnl_options = BorderedPanel(self)

		self.chk_md5 = CheckBoxESS(pnl_options, chkid.MD5, GT("Create md5sums file"),
				name="MD5", defaultValue=True, commands="md5sum")
		# The » character denotes that an alternate tooltip should be shown if the control is disabled
		self.chk_md5.tt_name = "md5»"
		self.chk_md5.col = 0

		# Option to strip binaries
		self.chk_strip = CheckBoxESS(pnl_options, chkid.STRIP, GT("Strip binaries"),
				name="strip»", defaultValue=True, commands="strip")
		self.chk_strip.col = 0

		# Deletes the temporary build tree
		self.chk_rmstage = CheckBoxESS(pnl_options, chkid.DELETE, GT("Delete staged directory"),
				name="RMSTAGE", defaultValue=True)
		self.chk_rmstage.col = 0

		# Checks the output .deb for errors
		self.chk_lint = CheckBoxESS(pnl_options, chkid.LINT, GT("Check package for errors with lintian"),
				name="LINTIAN", defaultValue=True, commands="lintian")
		self.chk_lint.tt_name = "lintian»"
		self.chk_lint.col = 0

		# Installs the deb on the system
		self.chk_install = CheckBox(pnl_options, chkid.INSTALL, GT("Install package after build"),
				name="INSTALL", commands=("gdebi-gtk", "gdebi-kde",))
		self.chk_install.tt_name = "install»"
		self.chk_install.col = 0

		# *** Lintian Overrides *** #

		if UsingTest("alpha"):
			# FIXME: Move next to lintian check box
			Logger.Info(__name__, "Enabling alpha feature \"lintian overrides\" option")
			self.lint_overrides = []
			btn_lint_overrides = CreateButton(self, label=GT("Lintian overrides"))
			btn_lint_overrides.Bind(wx.EVT_BUTTON, self.OnSetLintOverrides)

		btn_build = CreateButton(self, btnid.BUILD, GT("Build"), "build", 64)

		# Display log
		dsp_log = OutputLog(self)

		SetPageToolTips(self)

		# *** Event Handling *** #

		btn_build.Bind(wx.EVT_BUTTON, self.OnBuild)

		# *** Layout *** #

		lyt_options = wx.GridBagSizer()

		next_row = 0
		prev_row = next_row
		for CHK in pnl_options.Children:
			row = next_row
			FLAGS = lyt.PAD_LR

			if CHK.col:
				row = prev_row
				FLAGS = wx.RIGHT

			lyt_options.Add(CHK, (row, CHK.col), flag=FLAGS, border=5)

			if not CHK.col:
				prev_row = next_row
				next_row += 1

		pnl_options.SetSizer(lyt_options)
		pnl_options.SetAutoLayout(True)
		pnl_options.Layout()

		lyt_buttons = BoxSizer(wx.HORIZONTAL)
		lyt_buttons.Add(btn_build, 1)

		lyt_main = BoxSizer(wx.VERTICAL)
		lyt_main.AddSpacer(10)
		lyt_main.Add(wx.StaticText(self, label=GT("Extra Options")), 0,
				lyt.ALGN_LB|wx.LEFT, 5)
		lyt_main.Add(pnl_options, 0, wx.LEFT, 5)
		lyt_main.AddSpacer(5)

		if UsingTest("alpha"):
			#lyt_main.Add(wx.StaticText(self, label=GT("Lintian overrides")), 0, wx.LEFT, 5)
			lyt_main.Add(btn_lint_overrides, 0, wx.LEFT, 5)

		lyt_main.AddSpacer(5)
		lyt_main.Add(lyt_buttons, 0, lyt.ALGN_C)
		lyt_main.Add(dsp_log, 2, wx.EXPAND|wx.ALL, 5)

		self.SetAutoLayout(True)
		self.SetSizer(lyt_main)
		self.Layout()


	## Method that builds the actual Debian package
	#
	#  \param task_list
	#		\b \e dict : Task string IDs & page data
	#  \param build_path
	#		\b \e str : Directory where .deb will be output
	#  \param filename
	#		\b \e str : Basename of output file without .deb extension
	#  \return
	#		\b \e dbrerror : SUCCESS if build completed successfully
	def Build(self, task_list, build_path, filename):
		# Declare this here in case of error before progress dialog created
		build_progress = None

		try:
			# Other mandatory tasks that will be processed
			mandatory_tasks = (
				"stage",
				"install_size",
				"control",
				"build",
				)

			# Add other mandatory tasks
			for T in mandatory_tasks:
				task_list[T] = None

			task_count = len(task_list)

			# Add each file for updating progress dialog
			if "files" in task_list:
				task_count += len(task_list["files"])

			# Add each script for updating progress dialog
			if "scripts" in task_list:
				task_count += len(task_list["scripts"])

			if DebugEnabled():
				task_msg = GT("Total tasks: {}").format(task_count)
				print("DEBUG: [{}] {}".format(__name__, task_msg))
				for T in task_list:
					print("\t{}".format(T))

			create_changelog = "changelog" in task_list
			create_copyright = "copyright" in task_list

			pg_control = GetPage(pgid.CONTROL)
			pg_menu = GetPage(pgid.MENU)

			stage_dir = "{}/{}__dbp__".format(build_path, filename)

			if os.path.isdir("{}/DEBIAN".format(stage_dir)):
				try:
					shutil.rmtree(stage_dir)

				except OSError:
					ShowErrorDialog(GT("Could not free stage directory: {}").format(stage_dir),
							title=GT("Cannot Continue"))

					return (dbrerrno.EEXIST, None)

			# Actual path to new .deb
			deb = "\"{}/{}.deb\"".format(build_path, filename)

			progress = 0

			task_msg = GT("Preparing build tree")
			Logger.Debug(__name__, task_msg)

			wx.GetApp().Yield()
			build_progress = ProgressDialog(GetMainWindow(), GT("Building"), task_msg,
					maximum=task_count,
					style=PD_DEFAULT_STYLE|wx.PD_ELAPSED_TIME|wx.PD_ESTIMATED_TIME|wx.PD_CAN_ABORT)

			DIR_debian = ConcatPaths((stage_dir, "DEBIAN"))

			# Make a fresh build tree
			os.makedirs(DIR_debian)
			progress += 1

			if build_progress.WasCancelled():
				build_progress.Destroy()
				return (dbrerrno.ECNCLD, None)

			def UpdateProgress(current_task, message=None):
				task_eval = "{} / {}".format(current_task, task_count)

				if message:
					Logger.Debug(__name__, "{} ({})".format(message, task_eval))

					wx.GetApp().Yield()
					build_progress.Update(current_task, message)

					return

				wx.GetApp().Yield()
				build_progress.Update(current_task)

			# *** Files *** #
			if "files" in task_list:
				UpdateProgress(progress, GT("Copying files"))

				no_follow_link = GetField(GetPage(pgid.FILES), chkid.SYMLINK).IsChecked()

				# TODO: move this into a file functions module
				def _copy(f_src, f_tgt, exe=False):
					# NOTE: Python 3 appears to have follow_symlinks option for shutil.copy
					# FIXME: copying nested symbolic link may not work

					if os.path.isdir(f_src):
						if os.path.islink(f_src) and no_follow_link:
							Logger.Debug(__name__, "Adding directory symbolic link to stage: {}".format(f_tgt))

							os.symlink(os.readlink(f_src), f_tgt)
						else:
							Logger.Debug(__name__, "Adding directory to stage: {}".format(f_tgt))

							shutil.copytree(f_src, f_tgt)
							os.chmod(f_tgt, 0o0755)
					elif os.path.isfile(f_src):
						if os.path.islink(f_src) and no_follow_link:
							Logger.Debug(__name__, "Adding file symbolic link to stage: {}".format(f_tgt))

							os.symlink(os.readlink(f_src), f_tgt)
						else:
							if exe:
								Logger.Debug(__name__, "Adding executable to stage: {}".format(f_tgt))
							else:
								Logger.Debug(__name__, "Adding file to stage: {}".format(f_tgt))

							shutil.copy(f_src, f_tgt)

							# Set FILE permissions
							if exe:
								os.chmod(f_tgt, 0o0755)

							else:
								os.chmod(f_tgt, 0o0644)

				files_data = task_list["files"]
				for FILE in files_data:
					file_defs = FILE.split(" -> ")

					source_file = file_defs[0]
					target_file = "{}{}/{}".format(stage_dir, file_defs[2], file_defs[1])
					target_dir = os.path.dirname(target_file)

					if not os.path.isdir(target_dir):
						os.makedirs(target_dir)

					# Remove asteriks from exectuables
					exe = False
					if source_file[-1] == "*":
						exe = True
						source_file = source_file[:-1]

					_copy(source_file, "{}/{}".format(target_dir, os.path.basename(source_file)), exe)

					# Individual files
					progress += 1
					UpdateProgress(progress)

				# Entire file task
				progress += 1

			if build_progress.WasCancelled():
				build_progress.Destroy()
				return (dbrerrno.ECNCLD, None)

			# *** Strip files ***#
			# FIXME: Needs only be run if 'files' step is used
			if "strip" in task_list:
				UpdateProgress(progress, GT("Stripping binaries"))

				for ROOT, DIRS, FILES in os.walk(stage_dir): #@UnusedVariable
					for F in FILES:
						# Don't check files in DEBIAN directory
						if ROOT != DIR_debian:
							F = ConcatPaths((ROOT, F))

							if FileUnstripped(F):
								Logger.Debug(__name__, "Unstripped file: {}".format(F))

								# FIXME: Strip command should be set as class member?
								ExecuteCommand(GetExecutable("strip"), F)

				progress += 1

			if build_progress.WasCancelled():
				build_progress.Destroy()
				return (dbrerrno.ECNCLD, None)

			package = GetField(pg_control, inputid.PACKAGE).GetValue()

			# Make sure that the directory is available in which to place documentation
			if create_changelog or create_copyright:
				doc_dir = "{}/usr/share/doc/{}".format(stage_dir, package)
				if not os.path.isdir(doc_dir):
					os.makedirs(doc_dir)

			# *** Changelog *** #
			if create_changelog:
				UpdateProgress(progress, GT("Creating changelog"))

				# If changelog will be installed to default directory
				changelog_target = task_list["changelog"][0]
				if changelog_target == "STANDARD":
					changelog_target = ConcatPaths(("{}/usr/share/doc".format(stage_dir), package))

				else:
					changelog_target = ConcatPaths((stage_dir, changelog_target))

				if not os.path.isdir(changelog_target):
					os.makedirs(changelog_target)

				WriteFile("{}/changelog".format(changelog_target), task_list["changelog"][1])

				CMD_gzip = GetExecutable("gzip")

				if CMD_gzip:
					UpdateProgress(progress, GT("Compressing changelog"))
					res = subprocess.run([CMD_gzip, "-n", "--best", "{}/changelog".format(changelog_target)], stdout=subprocess.PIPE)
					if res.returncode != 0:
						ShowErrorDialog(GT("Could not compress changelog"), res.stdout.decode("utf-8"), warn=True, title=GT("Warning"))

				progress += 1

			if build_progress.WasCancelled():
				build_progress.Destroy()
				return (dbrerrno.ECNCLD, None)

			# *** Copyright *** #
			if create_copyright:
				UpdateProgress(progress, GT("Creating copyright"))

				WriteFile("{}/usr/share/doc/{}/copyright".format(stage_dir, package), task_list["copyright"])

				progress += 1

			if build_progress.WasCancelled():
				build_progress.Destroy()
				return (dbrerrno.ECNCLD, None)

			# Characters that should not be in filenames
			invalid_chars = (" ", "/")

			# *** Menu launcher *** #
			if "launcher" in task_list:
				UpdateProgress(progress, GT("Creating menu launcher"))

				# This might be changed later to set a custom directory
				menu_dir = "{}/usr/share/applications".format(stage_dir)

				menu_filename = pg_menu.GetOutputFilename()

				# Remove invalid characters from filename
				for char in invalid_chars:
					menu_filename = menu_filename.replace(char, "_")

				if not os.path.isdir(menu_dir):
					os.makedirs(menu_dir)

				WriteFile("{}/{}.desktop".format(menu_dir, menu_filename), task_list["launcher"])

				progress += 1

			if build_progress.WasCancelled():
				build_progress.Destroy()
				return (dbrerrno.ECNCLD, None)

			# *** md5sums file *** #
			# Good practice to create hashes before populating DEBIAN directory
			if "md5sums" in task_list:
				UpdateProgress(progress, GT("Creating md5sums"))

				if not WriteMD5(stage_dir, parent=build_progress):
					# Couldn't call md5sum command
					build_progress.Cancel()

				progress += 1

			if build_progress.WasCancelled():
				build_progress.Destroy()
				return (dbrerrno.ECNCLD, None)

			# *** Scripts *** #
			if "scripts" in task_list:
				UpdateProgress(progress, GT("Creating scripts"))

				scripts = task_list["scripts"]
				for SCRIPT in scripts:
					script_name = SCRIPT
					script_text = scripts[SCRIPT]

					script_filename = ConcatPaths((stage_dir, "DEBIAN", script_name))

					WriteFile(script_filename, script_text)

					# Make sure scipt path is wrapped in quotes to avoid whitespace errors
					# FIXME: both commands appear to do the same thing?
					os.chmod(script_filename, 0o0755)
					os.system(("chmod +x \"{}\"".format(script_filename)))

					# Individual scripts
					progress += 1
					UpdateProgress(progress)

				# Entire script task
				progress += 1

			if build_progress.WasCancelled():
				build_progress.Destroy()
				return (dbrerrno.ECNCLD, None)

			# *** Control file *** #
			UpdateProgress(progress, GT("Getting installed size"))

			# Get installed-size
			installed_size = os.popen(("du -hsk \"{}\"".format(stage_dir))).readlines()
			installed_size = installed_size[0].split("\t")
			installed_size = installed_size[0]

			# Insert Installed-Size into control file
			control_data = pg_control.Get().split("\n")
			control_data.insert(2, "Installed-Size: {}".format(installed_size))

			progress += 1

			if build_progress.WasCancelled():
				build_progress.Destroy()
				return (dbrerrno.ECNCLD, None)

			# Create final control file
			UpdateProgress(progress, GT("Creating control file"))

			# dpkg fails if there is no newline at end of file
			control_data = "\n".join(control_data).strip("\n")
			# Ensure there is only one empty trailing newline
			# Two '\n' to show physical empty line, but not required
			# Perhaps because string is not null terminated???
			control_data = "{}\n\n".format(control_data)

			WriteFile("{}/DEBIAN/control".format(stage_dir), control_data, noStrip="\n")

			progress += 1

			if build_progress.WasCancelled():
				build_progress.Destroy()
				return (dbrerrno.ECNCLD, None)

			# *** Final build *** #
			UpdateProgress(progress, GT("Running dpkg"))

			working_dir = os.path.split(stage_dir)[0]
			c_tree = os.path.split(stage_dir)[1]
			deb_package = "{}.deb".format(filename)

			# Move the working directory becuase dpkg seems to have problems with spaces in path
			os.chdir(working_dir)

			# HACK to fix file/dir permissions
			for ROOT, DIRS, FILES in os.walk(stage_dir):
				for D in DIRS:
					D = "{}/{}".format(ROOT, D)
					os.chmod(D, 0o0755)
				for F in FILES:
					F = "{}/{}".format(ROOT, F)
					if os.access(F, os.X_OK):
						os.chmod(F, 0o0755)
					else:
						os.chmod(F, 0o0644)

			# FIXME: Should check for working fakeroot & dpkg-deb executables
			res = subprocess.run([GetExecutable("fakeroot"), GetExecutable("dpkg-deb"), "-b", c_tree, deb_package])
			build_status = (res.returncode, res.stdout)

			progress += 1

			if build_progress.WasCancelled():
				build_progress.Destroy()
				return (dbrerrno.ECNCLD, None)

			# *** Delete staged directory *** #
			if "rmstage" in task_list:
				UpdateProgress(progress, GT("Removing temp directory"))

				try:
					shutil.rmtree(stage_dir)

				except OSError:
					ShowErrorDialog(GT("An error occurred when trying to delete the build tree"),
							parent=build_progress)

				progress += 1

			if build_progress.WasCancelled():
				build_progress.Destroy()
				return (dbrerrno.ECNCLD, None)

			# *** ERROR CHECK
			if "lintian" in task_list:
				UpdateProgress(progress, GT("Checking package for errors"))

				# FIXME: Should be set as class memeber?
				CMD_lintian = GetExecutable("lintian")
				errors = subprocess.run([CMD_lintian, deb]).stdout

				if errors != wx.EmptyString:
					e1 = GT("Lintian found some issues with the package.")
					e2 = GT("Details saved to {}").format(filename)

					WriteFile("{}/{}.lintian".format(build_path, filename), errors)

					DetailedMessageDialog(build_progress, GT("Lintian Errors"),
							ICON_INFORMATION, "{}\n{}.lintian".format(e1, e2), errors).ShowModal()

				progress += 1

			# Close progress dialog
			wx.GetApp().Yield()
			build_progress.Update(progress)
			build_progress.Destroy()

			# Build completed successfullly
			if not build_status[0]:
				return (dbrerrno.SUCCESS, deb_package)

			if PY_VER_MAJ <= 2:
				# Unicode decoder has trouble with certain characters. Replace any
				# non-decodable characters with � (0xFFFD).
				build_output = list(build_status[1])

				# String & unicode string incompatibilities
				index = 0
				for C in build_output:
					try:
						GS(C)

					except UnicodeDecodeError:
						build_output[index] = "�"

					index += 1

				build_status = (build_status[0], "".join(build_output))

			# Build failed
			return (build_status[0], build_status[1])

		except:
			if build_progress:
				build_progress.Destroy()

			return(dbrerrno.EUNKNOWN, traceback.format_exc())


	## TODO: Doxygen
	#
	#  \return
	#	\b \e tuple containing Return code & build details
	def BuildPrep(self):
		# Declare these here in case of error before dialogs created
		save_dia = None
		prebuild_progress = None

		try:
			# List of tasks for build process
			# 'stage' should be very first task
			task_list = {}

			# Control page
			pg_control = GetPage(pgid.CONTROL)
			fld_package = GetField(pg_control, inputid.PACKAGE)
			fld_version = GetField(pg_control, inputid.VERSION)
			fld_maint = GetField(pg_control, inputid.MAINTAINER)
			fld_email = GetField(pg_control, inputid.EMAIL)
			fields_control = (
				fld_package,
				fld_version,
				fld_maint,
				fld_email,
				)

			# Menu launcher page
			pg_launcher = GetPage(pgid.MENU)

			# Check to make sure that all required fields have values
			required = list(fields_control)

			if pg_launcher.IsOkay():
				task_list["launcher"] = pg_launcher.Get()

				required.append(GetField(pg_launcher, inputid.NAME))

				if not GetField(pg_launcher, chkid.FNAME).GetValue():
					required.append(GetField(pg_launcher, inputid.FNAME))

			for item in required:
				if TextIsEmpty(item.GetValue()):
					field_name = GT(item.GetName().title())
					page_name = pg_control.GetName()
					if item not in fields_control:
						page_name = pg_launcher.GetName()

					return (dbrerrno.FEMPTY, "{} ➜ {}".format(page_name, field_name))

			# Get information from control page for default filename
			package = fld_package.GetValue()
			# Remove whitespace
			package = package.strip(" \t")
			package = "-".join(package.split(" "))

			version = fld_version.GetValue()
			# Remove whitespace
			version = version.strip(" \t")
			version = "".join(version.split())

			arch = GetField(pg_control, inputid.ARCH).GetStringSelection()

			# Dialog for save destination
			ttype = GT("Debian packages")
			save_dia = wx.FileDialog(self, GT("Save"), os.getcwd(), wx.EmptyString, "{}|*.deb".format(ttype),
					wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT|wx.FD_CHANGE_DIR)
			save_dia.SetFilename("{}_{}_{}.deb".format(package, version, arch))
			if not save_dia.ShowModal() == wx.ID_OK:
				return (dbrerrno.ECNCLD, None)

			build_path = os.path.split(save_dia.GetPath())[0]
			filename = os.path.split(save_dia.GetPath())[1].split(".deb")[0]

			# Control, menu, & build pages not added to this list
			page_checks = (
				(pgid.FILES, "files"),
				(pgid.SCRIPTS, "scripts"),
				(pgid.CHANGELOG, "changelog"),
				(pgid.COPYRIGHT, "copyright"),
				)

			# Install step is not added to this list
			# 'control' should be after 'md5sums'
			# 'build' should be after 'control'
			other_checks = (
				(self.chk_md5, "md5sums"),
				(self.chk_strip, "strip"),
				(self.chk_rmstage, "rmstage"),
				(self.chk_lint, "lintian"),
				)

			prep_task_count = len(page_checks) + len(other_checks)

			progress = 0

			wx.GetApp().Yield()
			prebuild_progress = ProgressDialog(GetMainWindow(), GT("Preparing to build"),
					maximum=prep_task_count)

			if wx.MAJOR_VERSION < 3:
				# Resize dialog for better fit
				pb_size = prebuild_progress.GetSize().Get()
				pb_size = (pb_size[0]+200, pb_size[1])
				prebuild_progress.SetSize(pb_size)
				prebuild_progress.CenterOnParent()

			for PID, id_string in page_checks:
				wx.GetApp().Yield()
				prebuild_progress.Update(progress, GT("Checking {}").format(id_string))

				wizard_page = GetPage(PID)
				if wizard_page.IsOkay():
					task_list[id_string] = wizard_page.Get()

				progress += 1

			for task_check, id_string in other_checks:
				wx.GetApp().Yield()
				prebuild_progress.Update(progress, GT("Testing for: {}").format(task_check.GetLabel()))

				if task_check.GetValue():
					task_list[id_string] = None

				progress += 1

			# Close progress dialog
			wx.GetApp().Yield()
			prebuild_progress.Update(progress)
			prebuild_progress.Destroy()

			return (dbrerrno.SUCCESS, (task_list, build_path, filename))

		except:
			if save_dia:
				save_dia.Destroy()

			if prebuild_progress:
				prebuild_progress.Destroy()

			return (dbrerrno.EUNKNOWN, traceback.format_exc())


	## TODO: Doxygen
	def GetSaveData(self):
		build_list = []

		options = (
			self.chk_md5,
			self.chk_rmstage,
			self.chk_lint,
			)

		for O in options:
			if O.GetValue():
				build_list.append("1")

			else:
				build_list.append("0")

		if self.chk_strip.GetValue():
			build_list.append("strip")

		return "<<BUILD>>\n{}\n<</BUILD>>".format("\n".join(build_list))


	## Installs the built .deb package onto the system
	#
	#  Uses the system's package installer:
	#	gdebi if available or dpkg
	#
	#  Shows a success dialog if installed. Otherwise shows an
	#  error dialog.
	#  \param package
	#		\b \e str : Path to package to be installed
	def InstallPackage(self, package):
		system_installer = GetSystemInstaller()

		if not system_installer:
			ShowErrorDialog(
				GT("Cannot install package"),
				GT("A compatible package manager could not be found on the system"),
				__name__,
				warn=True
				)

			return

		Logger.Info(__name__, GT("Attempting to install package: {}").format(package))
		Logger.Info(__name__, GT("Installing with {}").format(system_installer))

		install_cmd = (system_installer, package,)

		wx.GetApp().Yield()
		# FIXME: Use ExecuteCommand here
		install_output = subprocess.Popen(install_cmd)

		# Command appears to not have been executed correctly
		if install_output == None:
			ShowErrorDialog(
				GT("Could not install package: {}"),
				GT("An unknown error occurred"),
				__name__
				)

			return

		# Command executed but did not return success code
		if install_output.returncode:
			err_details = (
				GT("Process returned code {}").format(install_output.returncode),
				GT("Command executed: {}").format(" ".join(install_cmd)),
				)

			ShowErrorDialog(
				GT("An error occurred during installation"),
				"\n".join(err_details),
				__name__
				)

			return


	## TODO: Doxygen
	def OnBuild(self, event=None):
		# Build preparation
		ret_code, build_prep = self.BuildPrep()

		if ret_code == dbrerrno.ECNCLD:
			return

		if ret_code == dbrerrno.FEMPTY:
			err_dia = DetailedMessageDialog(GetMainWindow(), GT("Cannot Continue"), ICON_EXCLAMATION,
					text="{}\n{}".format(GT("One of the required fields is empty:"), build_prep))
			err_dia.ShowModal()
			err_dia.Destroy()

			return

		if ret_code == dbrerrno.SUCCESS:
			task_list, build_path, filename = build_prep

			# Actual build
			ret_code, result = self.Build(task_list, build_path, filename)

			# FIXME: Check .deb package timestamp to confirm build success
			if ret_code == dbrerrno.SUCCESS:
				DetailedMessageDialog(GetMainWindow(), GT("Success"), ICON_INFORMATION,
						text=GT("Package created successfully")).ShowModal()

				# Installing the package
				if FieldEnabled(self.chk_install) and self.chk_install.GetValue():
					self.InstallPackage(result)

				return

			if result:
				ShowErrorDialog(GT("Package build failed"), result)

			else:
				ShowErrorDialog(GT("Package build failed with unknown error"))

			return

		if build_prep:
			ShowErrorDialog(GT("Build preparation failed"), build_prep)

		else:
			ShowErrorDialog(GT("Build preparation failed with unknown error"))


	## TODO: Doxygen
	#
	#  TODO: Show warning dialog that this could take a while
	#  TODO: Add cancel option to progress dialog
	#  FIXME: List should be cached so no need for re-scanning
	def OnSetLintOverrides(self, event=None):
		Logger.Debug(__name__, GT("Setting Lintian overrides..."))

		lintian_tags_file = "{}/data/lintian/tags".format(PATH_app)

		if not os.path.isfile(lintian_tags_file):
			Logger.Error(__name__, "Lintian tags file is missing: {}".format(lintian_tags_file))

			return False

		lint_tags = RemoveEmptyLines(ReadFile(lintian_tags_file, split=True))

		if lint_tags:
			Logger.Debug(__name__, "Lintian tags set")

			# DEBUG: Start
			if DebugEnabled() and len(lint_tags) > 50:
				print("  Reducing tag count to 200 ...")

				lint_tags = lint_tags[:50]

			Logger.Debug(__name__, "Processing {} tags".format(len(lint_tags)))
			# DEBUG: End


			tag_count = len(lint_tags)

			def GetProgressMessage(message, count=tag_count):
				return "{} ({} {})".format(message, count, GT("tags"))


			progress = TimedProgressDialog(GetMainWindow(), GT("Building Tag List"),
					GetProgressMessage(GT("Scanning default tags")))
			progress.Start()

			wx.GetApp().Yield()

			# Create the dialog
			overrides_dialog = CheckListDialog(GetMainWindow(), title=GT("Lintian Overrides"),
					allow_custom=True)
			# FIXME: Needs progress dialog
			overrides_dialog.InitCheckList(tuple(lint_tags))

			progress.SetMessage(GetProgressMessage(GT("Setting selected overrides")))

			for T in lint_tags:
				if T in self.lint_overrides:
					overrides_dialog.SetItemCheckedByLabel(T)
					self.lint_overrides.remove(T)

			progress.SetMessage(GetProgressMessage(GT("Adding custom tags"), len(self.lint_overrides)))

			# Remaining tags should be custom entries
			# FIXME:
			if self.lint_overrides:
				for T in self.lint_overrides:
					overrides_dialog.AddItem(T, True)

			progress.Stop()

			if overrides_dialog.ShowModal() == wx.ID_OK:
				# Remove old overrides
				self.lint_overrides = []
				for L in overrides_dialog.GetCheckedLabels():
					Logger.Debug(__name__, GT("Adding Lintian override: {}").format(L))

					self.lint_overrides.append(L)

			return True

		else:
			Logger.Debug(__name__, "Setting lintian tags failed")

			return False


	## TODO: Doxygen
	#
	#  TODO: Use string names in project file but retain
	#		compatibility with older projects that use
	#		integer values.
	def Set(self, data):
		# ???: Redundant
		self.Reset()
		build_data = data.split("\n")

		if GetExecutable("md5sum"):
			try:
				self.chk_md5.SetValue(int(build_data[0]))

			except IndexError:
				pass

		try:
			self.chk_rmstage.SetValue(int(build_data[1]))

		except IndexError:
			pass

		if GetExecutable("lintian"):
			try:
				self.chk_lint.SetValue(int(build_data[2]))

			except IndexError:
				pass

		self.chk_strip.SetValue(GetExecutable("strip") and "strip" in build_data)


	## TODO: Doxygen
	def SetSummary(self, event=None):
		pg_scripts = GetPage(pgid.SCRIPTS)

		# Make sure the page is not destroyed so no error is thrown
		if self:
			# Set summary when "Build" page is shown
			# Get the file count
			files_total = GetPage(pgid.FILES).GetFileCount()
			f = GT("File Count")
			file_count = "{}: {}".format(f, files_total)

			# Scripts to make
			scripts_to_make = []
			scripts = (("preinst", pg_scripts.chk_preinst),
				("postinst", pg_scripts.chk_postinst),
				("prerm", pg_scripts.chk_prerm),
				("postrm", pg_scripts.chk_postrm))

			for script in scripts:
				if script[1].IsChecked():
					scripts_to_make.append(script[0])

			s = GT("Scripts")
			if len(scripts_to_make):
				scripts_to_make = "{}: {}".format(s, ", ".join(scripts_to_make))

			else:
				scripts_to_make = "{}: 0".format(s)

			self.summary.SetValue("\n".join((file_count, scripts_to_make)))
