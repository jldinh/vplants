# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
DisplayAllNames, DisplayAllUserNames
	Display user or system variables and functions, ?, ??
Usage
	?
	? varname
	??
Arguments
	varname (STRING) : name of a user variable
Returned Object
	This function returns no value.
Description
	Command ? prints the content of an object identified by its name to the screen. If no name is given, the command prints the list of user variables. To print all the functions and variables defined in the system, use the command ??.
Note
	When using command ??, variables, constants of functions defined in the system are displayed with ':' as a prefix character. The names are sorted in alphabetical order.
See Also
	Display.

Examples
	AML>?
      No user object defined.
	AML> i=1
	<INT>1
	AML> ?
      i <INT> : 1
	AML> f(_x)=_x+1
      f <FUNC> : Function
	AML> ?
      f <FUNC> : Function
      i <INT> : 1
	AML> AML>?i
      i <INT> : 1
"""
