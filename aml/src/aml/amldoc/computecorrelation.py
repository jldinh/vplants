# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
ComputeCorrelation
	Computation of sample autocorrelation or cross-correlation functions.
  Usage
	ComputeCorrelation(seq1, MaxLag->10, Type->"Spearman"
	Normalization->"Exact")
	ComputeCorrelation(seqn, variable, MaxLag->10,
	Type->"Spearman", Normalization->"Exact")
	ComputeCorrelation(seqn, variable1, variable2, MaxLag->10,
	Type->"Spearman", Normalization->"Exact")	
  Arguments
	seq1 (sequences, discrete_sequences, markov_data, semi-markov_data): univariate sequences,
	seqn (sequences, discrete_sequences, markov_data, semi-markov_data): multivariate sequences,
	variable (int): variable index (computation of a sample autocorrelation function).
	variable1, variable2 (int): variable indices (computation of a sample cross-correlation function).
	
  Optional Arguments 
	Type (string): type of correlation coefficient: "Pearson" (linear correlation coefficient - default value), "Spearman" or "Kendall" (rank correlation coefficients).
	MaxLag (int): maximum lag. A default value is computed from the sequence length distribution,
	Normalization (STRING): normalization of the correlation coefficients: "Approximated" (the default - usual convention for time series analysis) or "Exact", (highly recommended for sample of short sequences). This optional argument can only be used if the optional argument Type is set at "Pearson" or "Spearman".
	
  Returned Object
	If variable, or variable1 and variable2 are valid indices of variables (and are different if two indices are given) 
    and if 0 < MaxLag < (maximum length of sequences), an object of type correlation is returned, otherwise no object is returned.	
  Background
	In the univariate case or if only variable is given, a sample autocorrelation function is computed. If variable1 and variable2 are given, a sample cross-correlation function is computed.
	
  See Also
	ComputePartialAutoCorrelation,
	ComputeWhiteNoiseAutoCorrelation.
"""
