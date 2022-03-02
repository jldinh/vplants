# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
TopParameters
	Construction of 'top' parameters from the three parameters or from an ASCII file.
  Usage
	TopParameters(proba, axillary_proba, rhythm_ratio,
	MaxPosition->40)
	
	TopParameters(file_name, MaxPosition->40)	
  Arguments
	proba (int, real): growth probability of the parent shoot,
	axillary_proba (int, real): growth probability of the offspring shoots,
	rhythm_ratio (int, real): growth rhythm ratio offspring shoots / parent shoot,
	
	file_name (string).
	
  Optional Arguments 
	MaxPosition (int): maximum position for the computation of the distributions of the number of internodes of offspring shoots (default value: 20).
	
  Returned Object
	If the construction succeeds, an object of type top_parameters is returned, otherwise no object is returned.
	
  Background
	The aim of the model of 'tops' is to related the growth of offspring shoots to the growth of their parent shoot in the case of immediate branching. In the case where the arguments are the three 'top' parameters, the constraints over these parameters are described in the definition of the syntactic form of the type top_parameters (cf. File Syntax).
	
  See Also
	Save, 
	Simulate ('top' parameters).
"""
