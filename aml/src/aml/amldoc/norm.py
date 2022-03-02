# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Norm
	Norm of an arrays.
Usage
	Norm(array)
Arguments
	array (ARRAY(REAL)). These two arrays must have identical size.
Returned Object
	The norm of an array is a REAL. If one of the arguments is Undef, returns Undef
Description
	Denote array=. The norm of arrays array is defined by: 
      
	
See Also
	
	EDist, 
	Angle, 
	SProd, 
	VProd, 
	Array.
	

Examples
AML>Norm([1.,0.,0.])
<REAL> 1
AML> Norm([1.,3.,0.,.4])
<REAL> 3.18748
"""
