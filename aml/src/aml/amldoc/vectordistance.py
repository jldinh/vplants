# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
VectorDistance
	Construction of an object of type vector_distance from types (and eventually weights) of variables or from an ASCII file.
  Usage
	VectorDistance(type1, type2,..., Distance->"QUADRATIC")
	VectorDistance(weight1, type1, weight2, type2,...,
	Distance->"QUADRATIC")
	
	VectorDistance(file_name)
	
  Arguments
	type1, type2, ... (string): variable types ("NUMERIC" ("N"), "ORDINAL" ("O") or "SYMBOLIC" ("S")),
	weight1, weight2, ... (real): weights of variables,
	
	file_name (string).
	
  Optional Arguments 
	Distance (string): distance type: "ABSOLUTE_VALUE" (the default) or "QUADRATIC". This optional argument is only relevant in the multivariate case.
	
  Returned Object
	If the construction succeeds, an object of type vector_distance is returned, otherwise no object is returned.	
  Background
	The type vector_distance implements standardization procedures. The objective of standardization is to avoid the dependence on the variable type (chosen among symbolic, ordinal, numeric and circular) and, for numeric variables, on the choice of the measurement units by converting the original variables to unitless variables.
	
  See Also
	
	Compare (vectors)
	Compare (sequences).
"""
