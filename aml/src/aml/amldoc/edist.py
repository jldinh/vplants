# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
EDist
	Euclidean distance between two points represented by two arrays.
Usage
	EDist(array)
Arguments
	array (ARRAY(REAL)). These two arrays must have identical size.
Returned Object
	The distance between two array is a REAL. If one of the arguments is Undef, returns Undef
Description
	Denote , . The norm of arrays array is defined by:
      
	
See Also
	
	Norm, 
	Angle, 
	SProd, 
	VProd, 
	Array.
	

Examples
    AML>EDist([1.,0.,0.],[1.,0.,10.])
	<REAL> 10
	AML> EDist([1.,0.],[0.,1.])
	<REAL> 1.41421
"""
