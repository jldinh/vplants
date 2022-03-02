# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
VProd
	Vectorial product of two arrays.
Usage
	VProd(a1, a2)
Arguments
	a1, a2 (ARRAY(REAL)). These two arrays must have dimension 3.
Returned Object
	The result of a vectorial product is an ARRAY(REAL) with the same dimension as a1 and a2. If one of the arguments is Undef, returns Undef
Description
	The function returns the vectorial product of two arrays in dimension 3. If a1 and a2, then  VProd(a1, a2) with 
	
	
Note
	Contrary to SProd, the dimension is limited here to 3.
See Also
	EDist, 
	Angle, 
	Norm, 
	Array.

Examples
	AML> VProd([1.,0.,0.],[0.,1.,0.])
	<ARRAY(REAL)> [0.,0.,1.]
	AML> SProd([0.,1.,0.],[1.,0.,0.])
    	<ARRAY(REAL)> [0.,0.,-1.]
"""
