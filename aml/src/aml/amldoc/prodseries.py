# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
ProdSeries
	Computes the series of incremental products associated with a given sequence of numerical values.
Usage
	ProdSeries(array)
Arguments
	array (ARRAY(T)). T is either INT or REAL. If the argument is Undef, returns Undef
Returned Object
	If array has type ARRAY(T), the function returns an element of type ARRAY(T), with the same number of elements. If the argument is Undef, returns Undef
Description
	Returns the mathematical series associated with the sequence of numerical values defined in array. Let array=, then the result is the array whose ith element is defined by . If array contains Undef elements, these elements are considered as having value 1 (they do not affect the overall product of other elements).
See Also
	
	Array, 
	Set, 
	Series, 
	Size, 
	Prod, 
	Sum.
	

Examples
	AML>ProdSeries([1,2,3,4])
	<ARRAY(INT)> [1,2,6,24]
	AML> ProdSeries([10,11,12,Undef,14,15])
	<ARRAY(INT)> [10,110,1320,1320,18480,277200]
"""
