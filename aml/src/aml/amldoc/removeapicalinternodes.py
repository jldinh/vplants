# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
RemoveApicalInternodes
	Removal of the apical internodes of the parent shoot of a 'top'.
  Usage
	RemoveApicalInternodes(top, nb_internode)	
  Arguments
	top (tops),
	nb_internode (int): number of removed internodes.
	
  Returned Object
	If nb_internode >  0 and if the removed internodes do not bear offspring shoots, an object of type tops is returned, otherwise no object is returned.
	
  See Also
	SelectIndividual, 
	Merge, 
	Reverse.
"""
