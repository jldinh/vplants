# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Tops
	Construction of a set of 'tops' from a multidimensional array of integers or from an ASCII file.
  Usage
	Tops(array, Identifiers->[1, 8, 12])
	
	Tops(file_name)	
  Arguments
	array (array(array(array(int)))),
	
	file_name (string).
	
  Optional Arguments 
	Identifiers (array(int)): identifiers of 'tops'. This optional argument can only be used if the first argument is of type array(array(array(int))).
	
  Returned Object
	If the construction succeeds, an object of type tops is returned, otherwise no object is returned.
  Description
	The data structure of type array(array(array(int))) should be constituted at the most internal level of arrays of size 2 (position of the offspring shoot on the parent shoot counted in number of nodes from the apex, number of internodes of the offspring shoot). Hence, the first component of successive elementary arrays (representing the index parameter) should be increasing. Note also that only the index parameter of the last array is considered.
	
  See Also
	Save, 
	Merge, 
	RemoveApicalInternodes, 
	Reverse, 
	SelectIndividual, 
	Estimate ('top' parameters).
"""
