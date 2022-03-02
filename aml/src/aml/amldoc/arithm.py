# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Arithmetic operators
	+,-,*,/ Classical arithmetic operators. Addition of a value to ARRAYs, SETs,
	LISTs, STRINGs and DATEs.
Usage
	a + b, a - b, a * b, a / b, - a : arithmetic operators.
	set +  val, set - val : physical addition of an element to a set object.
	stg1 + stg2 : contatenation of a character to a STRING.
	d1 + i, d1 -  i : addition of i time units to a date.
Arguments
	a,b (INT or REAL) : numerical values. For arithmetic operators, any combination of types INT and REAL is possible.
	set (ARRAY(T)) or set (SET(T)) or set (LIST(...)), val (T)
	stg1 (STRING), stg2 (STRING)
	d1 (DATE), i (INT).
Returned Object
	- For arithmetic operators, the result is INT only in the case where both a and b are INTs. Otherwise the result is REAL. If either a or b is Undef, returns Undef. A division by 0 returns an Undef value.
	- When an element is added to or removed from a set object set, the initial object is physically affected by the operation. The value returned by either these operators is the (modified) argument itself (and not a modification of a copy of the argument). If set is Undef, returns Undef. If set is not Undef and val is Undef, then the result
	- For a STRING, on the contrary, the concatenation of the two strings is a new STRING, different from both stg1 and stg2.
	- For date incrementation, cf. Date operators.
Description
	- If a and b are integer values, a / b performs an integral division. The arguments have to be casted to REALs if one wants to apply a division between arguments considered as REAL numbers.
	- '+' and '-' can be used to physically add or remove elements from a set object.
	- If set is an ARRAY, set + val makes the element val be appended at the end of set. set - val removes the first occurence of element val in the array set1.
	- '+' and '-' can be used to concatenate two strings.
	- '+' and '-' can be used for adding i time units to a date, cf. Date operators.
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
	AML># Arithmetic operators
	AML> 9 / 2
	<INT>4
	AML> 5 + 3
	<INT>8
	AML> 5.0 + 3
	<REAL>8
	AML> 9 / 0
	Undef
	AML> # Addition / Deletion of elements of set objects
	AML> a=[1,2,4,3,4,5,6,4]
	<ARRAY(INT)> [1,2,4,3,4,5,6,4]
	AML> a + 2
	<ARRAY(INT)> [1,2,4,3,4,5,6,4,2]
	AML> a
	<ARRAY(INT)> [1,2,4,3,4,5,6,4,2]
	AML> a - 4
	<ARRAY(INT)> [1,2,3,4,5,6,4,2]
	AML> a - 4
	<ARRAY(INT)> [1,2,3,5,6,4,2]
	AML> s=Set(1,2,4,3,4,5,6,4)
	<SET(INT)> [1,2,3,4,5,6]
	AML> s + 2
	<SET(INT)> [1,2,3,4,5,6]
	AML> s + 7
	<SET(INT)> [1,2,3,4,5,6,7]
	AML> s
	<SET(INT)> [1,2,3,4,5,6,7]
	AML> s - 2
	<SET(INT)> [1,3,4,5,6,7]
	AML> # Concatenation of strings
	AML> stg1 = "AMAP" ; stg2 = "mod"
	<STRING> mod
	AML> stg1 + stg2
	<STRING> AMAPmod
	AML> stg1
	<STRING> AMAP
"""
