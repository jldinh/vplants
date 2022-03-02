# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
ComputePartialAutoCorrelation
	Computation of sample partial autocorrelation functions.
  Usage
	ComputePartialAutoCorrelation(seq1, MaxLag->10,
	Type->"Kendall")  
	ComputePartialAutoCorrelation(seqn, variable, MaxLag->10,
	Type->"Kendall") 
	
  Arguments
	seq1 (sequences, discrete_sequences, markov_data, semi-markov_data): univariate sequences,
	seqn (sequences, discrete_sequences, markov_data, semi-markov_data): multivariate sequences,
	variable (int): variable index.
	
  Optional Arguments 
	MaxLag (int): maximum lag. A default value is computed from the sequence length distribution,
	Type (string): type of correlation coefficient: "Pearson" (linear correlation coefficient - the default) or "Kendall" (rank correlation coefficient).
	
  Returned Object
	If variable is a valid variable index and if 1 £ MaxLag < (maximum length of sequences), an object of type correlation is returned, otherwise no object is returned.	
  Background
	The partial autocorrelation coefficient at lag k measures the correlation between xi and xt+k not accounted for by  (or after adjusting for the effects of ).
	
  See Also
	ComputeCorrelation
"""
