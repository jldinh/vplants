# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Simulate
	Generation of a sample of sequences from a (hidden) Markovian process.
  Usage
	Simulate(markov, length_histo)
	Simulate(markov, size, length)
	Simulate(markov, size, seq)
	Simulate(semi_markov, length_histo, Counting->False)
	Simulate(semi_markov, size, length, Counting->False)
	Simulate(semi_markov, size, seq, Counting->False)	
  Arguments
	markov (markov, hidden_markov),
	semi_markov (semi-markov, hidden_semi-markov),
	length_histo (histogram, mixture_data, convolution_data, compound_data): frequency distribution of sequence lengths,
	size (int): sample size,
	length (int): sequence length,
	seq (discrete_sequences, markov_data, semi-markov_data),
	
  Optional Arguments 
	Counting (bool): computation of counting distributions (default value: True).
	
  Returned Object 
	
	 If the first argument is of type markov or hidden_markov, if 0 < (sample size) £ 100000, if (minimum sequence length) ³ 2, if (maximum sequence length) £ 1000 and if (cumulative sequence length) £ 1000000, an object of type markov_data is returned, otherwise no object is returned.
	 If the first argument is of type semi-markov or hidden_semi-markov, if 0 < (sample size) £ 100000, if (minimum sequence length) ³ 2, if (maximum sequence length) £ 1000 and if (cumulative sequence length) £ 1000000, an object of type semi-markov_data is returned, otherwise no object is returned.
	The returned object contains both the simulated sequences and the model used for simulation.
	
  Description
	If the third argument is of type discrete_sequences, markov_data or semi-markov_data, the simulated sequences has the same length distribution than the original sample given by this third argument. This simulation mode is particularly useful to study the effects of length biasing.
	
  See Also
	
	Markov,
	SemiMarkov,
	HiddenMarkov,
	HiddenSemiMarkov,
	ExtractHistogram.
"""
