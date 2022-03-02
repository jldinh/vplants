# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
EchoOn / EchoOff
	Put echo on during batch reading of a file
Usage
	EchoOn()
	EchoOff()
Arguments
	No argument.
Returned Object
	No returned value.
Description
	When a file is run in batch, using: aml -i filename
Description
	No output is made of the computations made within the file. It is possible to change this by writing in the file ''filename'' the command EchoOn(). As soon as it is read, aml outputs the results of subsequent computation on the standard output. The effect of this command can be cancelled by the command EchoOff().
Note
	These functions can be used for debugging a batch file as follows: in order to trace the different steps of a program, the user can call EchoOn() and insert debugging strings in the file. Since STRINGs objects are evaluated as strings of characters, the resulting STRING will be output to the standard output as soon as a STRING object is encountered in the batch file. When a particular debugging STRING is output to the screen, the user thus knows that a particular step of computation has been reached.
See Also
	Display

Examples
	# example of a batch file
	EchoOn()
	# string object which will be echoed to the screen,
	# indicating to the user which step of computation is being computed
	"step1"
	1+4
	"step2" # another debugging string
	+2
	EchoOff()
	Sqrt(10)
"""
