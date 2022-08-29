## \package command_line

# MIT licensing
# See: docs/LICENSE.txt


import sys

from startup.tests import available_tests
from startup.tests import test_list


## Solo args
#
#  -h or --help
#	Display usage information in the command line.
#  -v or --version
#	Display Debreate version in the command line & exit
solo_args = (
	("h", "help"),
	("v", "version"),
)

## Value args
#
#  -l or --log-level
#	Sets logging output level. Values can be 'quiet', 'info', 'warn', 'error', or debug,
#	or equivalent numeric values of 0-4. Default is 'error' (3).
#  -i or --log-interval
#	Set the refresh interval, in seconds, for updating the log window.
value_args = (
	("l", "log-level"),
	("i", "log-interval"),
)

cmds = (
	"clean",
	"compile",
	"legacy",
	"test",
)

parsed_args_s = []
parsed_args_v = {}
parsed_commands = []
parsed_path = None


def ArgOK(arg, group):
	for s, l in group:
		if arg in (s, l,):
			return True

	return False


def ArgIsDefined(arg, a_type):
	for group in (solo_args, value_args):
		for SET in group:
			for A in SET:
				if arg == A:
					return True

	return False


def GetArgType(arg):
	dashes = 0
	for C in arg:
		if C != "-":
			break

		dashes += 1

	if dashes:
		if dashes == 2 and len(arg.split("=")[0]) > 2:
			if not arg.count("="):
				return "long"

			if arg.count("=") == 1:
				return "long-value"

		elif dashes == 1 and len(arg.split("=")[0]) == 2:
			if not arg.count("="):
				return "short"

			if arg.count("=") == 1:
				return "short-value"

		return None

	if arg in cmds:
		return "command"

	# Any other arguments should be a filename path
	return "path"


def ParseArguments(arg_list):
	global parsed_path, parsed_commands, parsed_args_s, parsed_args_v

	if "test" in arg_list:
		testcmd_index = arg_list.index("test")
		tests = arg_list[testcmd_index+1:]

		if not tests:
			print("ERROR: Must supply at least one test")
			sys.exit(1)

		for TEST in tests:
			if TEST not in available_tests:
				print("ERROR: Unrecognized test: {}".format(TEST))
				sys.exit(1)

			test_list.append(TEST)

			# Remove tests from arguments
			arg_list.pop(testcmd_index + 1)

		# Remove test command from arguments
		arg_list.pop(testcmd_index)

	argc = len(arg_list)

	for AINDEX in range(argc):
		if AINDEX >= argc:
			break

		A = arg_list[AINDEX]
		arg_type = GetArgType(A)

		if arg_type == None:
			print("ERROR: Malformed argument: {}".format(A))
			sys.exit(1)

		if arg_type == "command":
			parsed_commands.append(A)
			continue

		if arg_type == "path":
			if parsed_path != None:
				print("ERROR: Extra input file detected: {}".format(A))
				# FIXME: Use errno here
				sys.exit(1)

			parsed_path = A
			continue

		clip = 0
		for C in A:
			if C != "-":
				break

			clip += 1

		if arg_type in ("long", "short"):
			parsed_args_s.append(A[clip:])
			continue

		# Anything else should be a value type
		key, value = A.split("=")

		# FIXME: Value args can be declared multiple times

		if not value.strip():
			print("ERROR: Value argument with empty value: {}".format(key))
			# FIXME: Use errno here
			sys.exit(1)

		key = key[clip:]

		# Use long form
		for S, L in value_args:
			if key == S:
				key = L
				break

		# Allow using 'warning' as 'alias' for 'log-level'
		if key == "log-level" and value == "warning":
			value = "warn"

		parsed_args_v[key] = value

	for A in parsed_args_s:
		if not ArgOK(A, solo_args):
			for S, L in value_args:
				if A in (S, L,):
					print("ERROR: Value argument with empty value: {}".format(A))
					# FIXME: Use errno here:
					sys.exit(1)

			print("ERROR: Unknown argument: {}".format(A))
			# FIXME: Use errno here
			sys.exit(1)

		# Use long form
		arg_index = parsed_args_s.index(A)
		for S, L in solo_args:
			if A == S:
				parsed_args_s[arg_index] = L

	for A in parsed_args_v:
		if not ArgOK(A, value_args):
			print("ERROR: Unknown argument: {}".format(A))
			# FIXME: Use errno here
			sys.exit(1)

	for S, L in solo_args:
		s_count = parsed_args_s.count(S)
		l_count = parsed_args_s.count(L)

		if s_count + l_count > 1:
			print("ERROR: Duplicate arguments: -{}|--{}".format(S, L))
			# FIXME: Use errno here
			sys.exit(1)


## Checks if an argument was used
def FoundArg(arg):
	for group in (parsed_args_s, parsed_args_v):
		for A in group:
			if A == arg:
				return True

	return False


## Checks if a command was used
def FoundCmd(cmd):
	return cmd in parsed_commands


def GetParsedPath():
	return parsed_path
