# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Echo
	Displays messages on the screen
Usage
	Echo(arg1,arg2,...,argi,...,argn)
Arguments
	argi (ANY) : the ith arg (i = 1...n) can be of any type. The number of argument n is arbitrary, provided it is greater than or equal to 1.
Optional Arguments
	ByteSize (INT) : This optional argument must be used when the size of the string representing an object in the list of arguments exceeds 10000 bytes (you are warned by a message whenever this occurs).
Returned Object
	STRING
Description
	This function can be used to build messages during some AML function computation. This is helpful while debugging AML functions to store and display intermediate results.
Note
	These functions can be used for debugging a batch file as follows: in order to trace the different steps of a program, the user can call EchoOn() and insert debugging strings in the file. Since STRINGs objects are evaluated as strings of characters, the resulting STRING will be output to the standard output as soon as a STRING object is encountered in the batch file. When a particular debugging STRING is output to the screen, the user thus knows that a particular step of computation has been reached.
See Also
	Display,
	EchoOn,
	EchoOff,
	

Examples
	AML>a = [1,2,3]
	AML>Echo("array a = ", a, "has a size = ", Size(_a))

	AML>f(_x) = Switch _x \
	AML>Case 1: Green
	AML>Case 2: Red
	AML>Case 3: Yellow
	AML>Default: (m=Echo("Color not found for value ", _x);Black)

	AML>f(2)
	<INT> 3	# code for Red
	AML>m
	<STRING> m

	AML>f(7)
	<INT> 0	# code for Black
	AML>m
	<STRING> "Color not found for value 7"
"""
