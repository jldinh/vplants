# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
SetMinus
	Difference between to set objects, -
Usage
	SetMinus(set1,set2)
Arguments
	set1,set2 (ARRAY or SET) : these two arguments must have the same type
Returned Object
	SetMinus returns a set object of the same type as its two arguments, i.e. either ARRAY or SET. If either set1 or set2 is Undef, returns Undef.
Description
	SetMinus(set1,set2) returns the set object made up by the objects of set1 that are not in set2 If set1 and set2 are ARRAYs, SetMinus(set1,set2) preserves in the resulting ARRAY the order of elements of set1.
Note
	
	SetMinus can also be invoked with the minus sign -.

Examples
	AML>SetMinus([1,2,3],[3,1,4])
	<ARRAY(ANY)>[2]
	AML> SetMinus(Set(1,2,3,4,5),Set(1,3,5,6,7))
	<SET(ANY)>[2,4]
"""
