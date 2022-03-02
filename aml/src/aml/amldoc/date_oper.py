# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Date operators
	+ , -, Second, Minute, Hour, Day, DateUnit, DateFormat, Date, ToTimeUnit.
Usage
	d1 + nb
	d1 - nb
	d1 - d2
	Date(stg)
	ToTimeUnit(i)
Arguments
	d1, d2 (DATE)
	nb, i (INT)
	stg
	Second, Minute, Hour, Day (INT): definition of classical date units in terms of integers.
	DateUnit(INT): value of the current date unit.
	DateFormat(STRING): STRING indicating the format of dates currently used in the system.
Returned Object
	The addition/substraction of a date and an integer returns a DATE. The new date is the old date incremented/decremented by nb times DateUnit.
	The difference between two dates returns an INT corresponding to the number of DateUnit between these two dates. This difference can be a negative integer.
	Second = 1, Minute = 60, Hour = 3600, Day = 86400 are global constant values.
	Global variables and their default values: DateFormat = ''DDMMYY'', DateUnit = 86400. These values are used as parameters by other date functions.
	The value returned by Date() is an INT corresponding to the integer encoding of a date defined as a STRING. If stg is Undef, returns Undef.
	The value returned by ToTimeUnit is the conversion of number i into a corresponding number of DateUnits. If i is Undef, returns Undef.
Description
	DateUnit is given the default value Day. It may be changed to other values, for example DateUnit = Hour. Once a DateUnit is fixed, other date functions can be used. The DateUnit is implicitly used as a global variable by the other functions when necessary (e.g. in incrementation of dates, or integer conversions to dates).
	Function Date() converts a STRING into a date. It uses the current value of DateFormat to encode strings as DATE objects. Valid values of DateFormat are strings: ''DDMM'', ''DDMMYY'', ''MMYY'', ''DDMMTIME'', ''DDMMYYTIME''. A date STRING with format DDMMYY is a STRING like ''09/07/97'', where '/' is a mandatory separator between date fields. A time STRING is a series of 1 to 3 integers separated by a ':'. Valid time strings are ''12:35:01'', ''12:35:'', ''12:35'' or ''12''. Whenever time information is used, e.g. DateFormat = DDMMTIME, valid time strings have to be concatenated to date strings, separated by a white space: e.g. ''09/07 12:35:01''.
Note
	Dates have to be greater than 01/01/1901.
See Also
	MTG module: 
	DateSample, 
	FirstDefinedFeature, 
	LastDefinedFeature, 
	NextDate, 
	PreviousDate
	

Examples
	AML>DateUnit
	<INT>86400
	AML> DateFormat
	<STRING>DDMMTIME
	AML> d1 = Date("10/0912:33")
	<DATE> 10/09 12:33
	AML> DateFormat
	<STRING>DDMMYY
	AML> d1 = Date("10/09/97")
	<DATE> 10/09/97
	AML> # Adding 10 days to d1
	AML> d2 = d1 + 10
	<DATE> 20/09/97
	AML> d2 - d1
	<INT>10
	AML> DateUnit = Minute
	<INT>60
	AML> ToTimeUnit(420)
	<INT>7
"""
