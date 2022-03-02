# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Markov
	Construction of a Markov chain from an ASCII file.
  Usage
	Markov(file_name, Length->40)	
  Arguments
	file_name (string).
	
  Optional Arguments 
	Length (int): length of sequences for the computation of the intensity and counting characteristic distributions (default value: 20).
	
  Returned Object
	If the construction succeeds, an object of type markov is returned, otherwise no object is returned.	
  Background
	The type markov covers both homogeneous Markov chains and non-homogeneous Markov chains. A Markov chain is said to be non-homogeneous if for at least one state, the self-transition probability is related to the index parameter by a simple parametric function (monomolecular or logistic).
	
  See Also
	Save, 
	Compare (Markovian models for sequences), 
	Compare (Markovian models), 
	Simulate (Markovian models).
"""
