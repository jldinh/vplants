# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Append
	Appends a value to ARRAYs, SETs, STRINGs.
Usage
	Append(set, val)
	Append(stg1, stg2)
Arguments
	set (ARRAY(T)) or set (SET(T)) or set (LIST(...)),
	val (T), value that must be appended at the end of set.
	stg1, stg2 (STRING): contatenation of a character to a STRING.
Returned Object
	- When an element appended to a set object set, the initial object is physically affected by the operation. The value returned is the (modified) argument itself (and not a modification of a copy of the argument). If set is Undef, returns Undef. If set is not Undef and val is Undef, then Undef is appended to the argument.
	- For a STRING, on the contrary, the concatenation of the two strings is a new STRING, different from both stg1 and stg2.
Description
	If set is an ARRAY, Append(set,val) makes the element val beappended at the end of set.
Side Effect
	Important: contrary to most functions in AML which leave their argument unchanged, this fonction modifies its set argument. The value returned is the modified argument.
See Also
	
	Union, 
	Inter, 
	SetMinus, 
	Date operators, 
	ToSet, 
	ToArray.
	

Examples
	AML>a=[1,2,4,3,4,5,6,4]
	<ARRAY(INT)> [1,2,4,3,4,5,6,4]
	AML> Append(a,2)
	<ARRAY(INT)> [1,2,4,3,4,5,6,4,2]
	AML> a
	<ARRAY(INT)> [1,2,4,3,4,5,6,4,2]
	AML> s=Set(1,2,4,3,4,5,6,4)
	<SET(INT)> [1,2,3,4,5,6]
	AML> Append(s,2)
	<SET(INT)> [1,2,3,4,5,6]
	AML> Append(s,7)
	<SET(INT)> [1,2,3,4,5,6,7]
	AML> s
	<SET(INT)> [1,2,3,4,5,6,7]
	AML> # Concatenation of strings
	AML> stg1="AMAP";stg2="mod"
	<STRING> mod
	AML> Append(stg1,stg2)
	<STRING> AMAPmod
	AML> stg1
	<STRING> AMAP
"""
