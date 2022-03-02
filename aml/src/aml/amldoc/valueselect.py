# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
ValueSelect
	Selection of individuals according to the values taken by a variable.
  Usage
	ValueSelect(histo, value, Mode->"Reject")
	ValueSelect(histo, min_value, max_valueMode->"Reject")
	
	ValueSelect(vec1, value, Mode->"Reject")
	ValueSelect(vec1, min_value, max_value, Mode->"Reject")
	ValueSelect(vecn, variable, value, Mode->"Reject")
	ValueSelect(vecn, variable, min_value, max_value,
	Mode->"Reject")
	
	ValueSelect(seq1, value, Mode->"Reject")
	ValueSelect(seq1, min_value, max_value, Mode->"Reject")
	ValueSelect(seqn, variable, value, Mode->"Reject")
	ValueSelect(seqn, variable, min_value, max_value,
	Mode->"Reject")
	
  Arguments
	histo (histogram, mixture_data, convolution_data, compound_data),
	
	value (int): value,
	min_value (int): minimum value,
	max_value (int): maximum value,
	
	vec1 (vectors): values,
	vecn (vectors): vectors,
	variable (int): variable index,
	
	seq1 (sequences, discrete_sequences, markov_data, semi-markov_data): univariate sequences,
	seqn (sequences, discrete_sequences, markov_data, semi-markov_data): multivariate sequences.
	
  Optional Arguments 
	Mode (string): conservation or rejection of selected individuals: "Keep" (the default) or "Reject".
	
  Returned Object
	If either value >= 0 or if 0 <= min_value <= max_value and if the range of values defined either by value or by min_value and max_value enables to select individuals, an object of type HISTOGRAM is returned (respectively vectors, sequences or discrete_sequences), otherwise no object is returned. In the case of a first argument of type sequences, discrete_sequences, markov_data or semi-markov_data, the returned object is of type discrete_sequences if all the variables are of type STATE, if the possible values for each variable are consecutive from 0 and if the number of possible values for each variable is <= 15.
	
  See Also
	Cluster, 
	Merge, 
	Shift, 
	Transcode, 
	SelectIndividual, 
	MergeVariable, 
	SelectVariable, 
	Cumulate, 
	Difference, 
	IndexExtract, 
	LengthSelect, 
	MovingAverage, 
	RecurrenceTimeSequences, 
	RemoveRun, 
	Reverse, 
	SegmentationExtract,
	VariableScaling.
"""
