# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
HiddenSemiMarkov
	Construction of an object of type hidden_semi-markov from an ASCII file.
  Usage
	HiddenSemiMarkov(file_name, Length->40, Counting->False)	
  Arguments
	file_name (string)
	
  Optional Arguments 
	Length (int): length of sequences for the computation of the intensity and counting characteristic distributions (default value: 20),
	Counting (bool): computation of counting characteristic distributions (default value: True).
	
  Returned Object
	If the construction succeeds, an object of type hidden_semi-markov is returned, otherwise no object is returned.	
  Background
	A hidden semi-Markov chain is constructed from an underlying semi-Markov chain (first-order Markov chain representing transition between distinct states and state occupancy distributions associated to the nonabsorbing states) and nonparametric observation (or state-dependent) distributions. The state occupancy distributions are defined as object of type distribution with the additional constraint that the minimum time spent in a given state is 1 (inf_bound <= 1).
	
  See Also
	Save, 
	Compare (Markovian models for sequences), 
	Compare (Markovian models), 
	Estimate (Markovian models), 
	ComputeStateSequences, 
	Simulate (Markovian models).
"""
