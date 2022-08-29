## \package globals.strings
#
#  Module for manipulating strings & string lists

# MIT licensing
# See: docs/LICENSE.txt


import sys


## Checks if a text string is empty
#
#  \param text
#		The string to be checked
def TextIsEmpty(text):
	return not text.strip(" \t\n\r")


## Removes empty lines from a string or string list
#
#  \param text
#	\b \e String or \b \e list to be checked
#  \return
#	\b \e String or \b \e tuple with empty lines removed
def RemoveEmptyLines(text):
	fmt_string = False

	if IsString(text):
		fmt_string = True
		text = text.split("\n")

	elif isinstance(text, tuple):
		text = list(text)

	# Iterate in reverse to avoid skipping indexes
	for INDEX in reversed(range(len(text))):
		if TextIsEmpty(text[INDEX]):
			text.pop(INDEX)

	if fmt_string:
		return "\n".join(text)

	return tuple(text)


## Checks if object is a string instance
#
#  Compatibility function for legacy Python versions
#
#  FIXME: deprecated
def IsString(text):
	return isinstance(text, str)


## Converts an object to a string instance
#
#  Compatibility function for legacy Python versions
#
#  FIXME: deprecated
#
#  \param item
#	Instance to be converted to string
#  \return
#	Compatible string
def ToString(item):
	return str(item)


GS = str


## Tests if a string can be converted to int or float
#
#  \param string
#	\b \e String to be tested
def StringIsNumeric(string):
	try:
		float(string)
		return True

	except ValueError:
		return False


## Tests if a string is formatted for versioning
def StringIsVersioned(string):
	for P in string.split("."):
		if not P.isnumeric():
			return False

	return True


## Retrieves a class instance's module name string
#
#  \param item
#	Object instance
#  \param className
#	If <b><i>True</i></b>, returns class object's name instead of module name
#  \param full
#	If <b><i>True</i></b>, return entire module/class string without parsing
def GetModuleString(item, className=False, full=False):
	module = ToString(item.__class__)

	# Strip extra characters
	if "'" in module:
		module = module[module.index("'")+1:].split("'")[0]

	if full:
		return module

	module = module.split(".")

	if className:
		return module[-1]

	return ".".join(module[:-1])


## Retrieves an instance's method name in the format of "Class.Method"
#
#  \param function
#	Function object
#  \param includeModule
#	Prepend module name to string for class methods
def GetFunctionString(function, includeModule=False):
	function = ToString(function).strip("<>")

	if function.startswith("bound method "):
		function = function.split("<")

		module = function[1].split(";")[0]
		function = function[0].lstrip("bound method ").split(" ")[0]

		if includeModule:
			class_name = function.split(".")[0]

			if ".{}".format(class_name) in module:
				module = module.replace(".{}".format(class_name), "")

			function = "{}.{}".format(module, function)

	else:
		function = function.split(" ")[1]

	return function
