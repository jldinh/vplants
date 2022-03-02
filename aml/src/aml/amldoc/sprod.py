# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
SProd
	Scalar product of two arrays.
Usage
	SProd(a1, a2)
Arguments
	a1, a2 (ARRAY(REAL)). These two arrays must have identical size.
Returned Object
	The result of a scalar product is a REAL. If one of the arguments is Undef, returns Undef
Description
	Denote a1 and a2. The scalar product of two arrays with same dimension n is defined by: 
	
	
See Also
	
	EDist, 
	Angle, 
	Norm, 
	VProd, 
	Array.

Examples
	AML>SProd([1.,0.,0.],[0.,1.,0.])
	<REAL> 0
	AML> SProd([1.,1.,0.,4.],[1.,1.,0.,2.])
	<REAL> 10
"""
