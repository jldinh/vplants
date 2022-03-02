# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Vectors
	Construction of a set of vectors from a multidimensional array, from a set of sequences or from an ASCII file.
  Usage
	Vectors(array, Identifiers->[1, 8, 12])
	
	Vectors(seq, IndexVariable->True)
	
	Vectors(file_name)	
  Arguments
	array (array(array(int))),
	
	seq (sequences, discrete_sequences, markov_data, semi-markov_data),
	
	file_name (string).
	
  Optional Arguments 
	Identifiers (array(int)): explicit identifiers of vectors. This optional argument can only be used if the first mandatory argument is of type array(array(int)).
	IndexVariable (bool): taking into account of the implicit index parameter as a supplementary variable (default value: False). This optional argument can only be used if the first mandatory argument is of type sequences, discrete_sequences, markov_data or semi-markov_data.
	
  Returned Object
	If the construction succeeds, an object of type vectors is returned, otherwise no object is returned.
   Description
	The data structure of type array(array(int)) should be constituted at the most internal level of arrays of constant size.
	
  See Also
	Save, 
	ExtractHistogram, 
	Cluster, 
	Merge, 
	MergeVariable, 
	SelectIndividual, 
	SelectVariable, 
	Shift, 
	Transcode, 
	ValueSelect, 
	Compare (vectors),  
	ComputeRankCorrelation, 
	ContingencyTable, 
	Regression, 
	VarianceAnalysis.
"""
