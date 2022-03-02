# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Max
	Computes the maximum value of the elements of an array or a set.
Usage
	Max(array)
Arguments
	array (ARRAY(T) or SET(T)). T is either INT or REAL. If the argument is Undef, returns Undef
Returned Object
	If array has type ARRAY(T) or SET(T), the function returns an element of type T. If the argument is Undef, returns Undef
Description
	Returns the element whose value is maximum over the set of elements of array. If array contains Undef elements, these elements are discarded.
See Also
	
	Array, 
	Set, 
	Series, 
	Size, 
	Sum, 
	Min.
	

Examples
    AML>Max([10,11,12,13,14,15])
	<INT> 15
	AML> Max([2,2,Undef,7,1])
	<INT> 7
	AML> Max(Foreach _x In[0:Pi:Pi/100] : Cos(_x))
	<REAL> 1
"""
