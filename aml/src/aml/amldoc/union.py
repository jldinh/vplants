# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Union
	Union of to set objects, |
Usage
	Union(set1,set2)
	set1 | set2
Arguments
	set1, set2 (ARRAY or SET) : these two arguments must have the same type
Returned Object
	Union returns a set object of the same type as its two arguments, i.e. either ARRAY or SET. If either set1 or set2 is Undef, returns Undef.
Description
	Union(set1,set2) returns the set object made up by the objects of set1 and of set2. If set1 and set2 are ARRAYs, Union(set1,set2) concatenates the two arrays.
Note
	Union can also be invoked with the minus sign |.
See Also
	Inter, 
	ToSet, 
	ToArray, 
	Sort,
	Merge.


Examples
	AML> Union([1,2],[0,2,3,4])
	<ARRAY(ANY)>[1,2,0,2,3,4]
	AML> Union(Set(1,2),Set(0,2,3,4))
	<SET(ANY)>[0,1,2,3,4]
"""
