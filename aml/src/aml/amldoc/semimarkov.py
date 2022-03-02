# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
SemiMarkov
	Construction of a semi-Markov chain from an ASCII file.
  Usage
	SemiMarkov(file_name, Length->40, Counting->True)	
  Arguments
	file_name (string).
	
  Optional Arguments 
	Length (int): length of sequences for the computation of the intensity and counting characteristic distributions (default value: 20),
	Counting (bool): computation of counting characteristic distributions (default value: True).
	
  Returned Object
	If the construction succeeds, an object of type semi-markov is returned, otherwise no object is returned.	
  Background
	A semi-Markov chain is constructed from a first-order Markov chain representing transition between distinct states and state occupancy distributions associated to the nonabsorbing states. The state occupancy distributions are defined as object of type distribution with the additional constraint that the minimum time spent in a given state is at least 1 (inf_bound >= 1).
	
  See Also
	Save, 
	Compare (Markovian models for sequences), 
	Compare (Markovian models), 
	Simulate (Markovian models).
"""
