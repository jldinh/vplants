# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
HiddenMarkov
	Construction of an object of type hidden_markov from an ASCII file.
  Usage
	HiddenMarkov(file_name, Length->40)	
  Arguments
	file_name (string)
	
  Optional Arguments 
	Length (int): length of sequences for the computation of the intensity and counting characteristic distributions (default value: 20).
	
  Returned Object
	If the construction succeeds, an object of type hidden_markov is returned, otherwise no object is returned.	
  Background
	A hidden Markov chain is constructed from an underlying Markov chain and nonparametric observation (or state-dependent) distributions.
	
  See Also
	Save, 
	Compare (Markovian models for sequences), 
	Compare (Markovian models), 
	Estimate (Markovian models), 
	ComputeStateSequences, 
	Simulate (Markovian models).
"""
