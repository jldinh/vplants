# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Angle
	Angle made by the vectors corresponding to two arrays of reals.
Usage
	Angle(a1, a2)
Arguments
	a1, a2 (ARRAY(REAL)). These two arrays must have identical size.
Returned Object
	The result is an angle expressed in radians (real between 0 and Pi). If one of the arguments is Undef, returns Undef. If the dimension is 0 the result is Undef.
Description
	Angle made by the vectors corresponding to two arrays of reals.
See Also
	
	Edist, 
	SProd, 
	Norm, 
	VProd, 
	Array.
	

Examples
	AML>Angle([1.,0.,0.],[0.,1.,0.])
	<REAL> 1.5708
	AML> Angle([1.,0.,0.],[1.,1.,1])
	<REAL> 0.955317
"""
