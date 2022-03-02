# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Simulate
	Generation of 'tops' from 'top' parameters.
  Usage
	Simulate(top_param, size, nb_trial, NbAxillary->2)	
  Arguments
	top_param (top_parameters),
	size (int): sample size,
	nb_trial (int): number of Bernoulli trials for the growth of the parent shoot,
	
  Optional Arguments 
	NbAxillary (int): number of offspring shoots per node (default value: 1, should be £ 4).
	
  Returned Object
	If 0 < size £ 100000 and if 0 < nb_trial £ 1000, an object of type tops is returned, otherwise no object is returned. The returned object contains both the simulated 'tops' and the model used for simulation.
	
  See Also
	
	TopParameter,
	ExtractHistogram.
"""
