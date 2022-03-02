# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Inter
	Intersection of to set objects, &
Usage
	Inter(set1, set2)
	set1 & set2
Arguments
	set1, set2 (ARRAY or SET) : these two arguments must have the same type
Returned Object
	Inter returns a set object of the same type as its two arguments, i.e. either ARRAY or SET. If either set1 or set2 is Undef, returns Undef.
Description
	Inter(set1, set2) returns the set object made up by the objects that both belong to set1 and to set2. If set1 and set2 are ARRAYs, Inter() preserves the order of object from set2.
Note
	Inter can also be invoked with the minus sign &.
See Also
	
	Union, 
	ToSet, 
	ToArray, 
	Sort.
	

Examples
    AML>Inter( [1,2,3,4,5,6,7],[0,2,3,4,10])
	<ARRAY(ANY)>[2,3,4]
	AML> Inter_set = [1,2,3,4,5,6,7] & [0,3,2,4,10]
	<ARRAY(ANY)>[3,2,4]
	AML> Set (1,2,3,4,5,6,7) & Set(0,3,2,4,10)
	<set(ANY)>[2,3,4]
"""
