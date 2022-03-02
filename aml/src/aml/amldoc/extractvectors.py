# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
ExtractVectors
	Extraction of vectors from global characteristics of sequences (length or counting characteristics).
  Usage
	ExtractVectors(seq, "Length")
	ExtractVectors(seq1, "NbRun", value)
	ExtractVectors(seq1, "NbOccurrence", value)
	ExtractVectors(seqn, "NbRun", variable, value)
	ExtractVectors(seqn, "NbOccurrence", variable, value)	
  Arguments
	seq (sequences, discrete_sequences, markov_data, semi-markov_data),
	seq1 (discrete_sequences, markov_data, semi-markov_data): univariate sequences,
	seqn (discrete_sequences, markov_data, semi-markov_data): multivariate sequences,
	value (int): value,
	variable (int): variable index.
	
  Returned Object
	An object of type vectors is returned.
  Description
	The type of global characteristic is given by a key word chosen among "Length", "NbRun" or "NbOccurrence". In the case of counting characteristics, the key word "NbRun" or "NbOccurrence" should be followed by a variable index in the case of multivariate sequences, and by the value of interest.
	
  See Also
	
	ExtractHistogram, 
	Plot, 
	MergeVariable, 
	Compare (renewal process), 
	ContingencyTable, 
	Regression, 
	Varianceanalysis.
"""
