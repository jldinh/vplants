# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
RecurrenceTimeSequences
	Computation of recurrence time sequences for a given value (and for a given variable).
  Usage
	RecurrenceTimeSequences(seq1, value)
	RecurrenceTimeSequences(seqn, variable, value)	
  Arguments
	seq1 (sequences, discrete_sequences, markov_data, semi-markov_data): univariate sequences,
	seqn (sequences, discrete_sequences, markov_data, semi-markov_data): multivariate sequences,
	variable (int): variable index,
	value (int): value.
	
  Returned Object
	If the selected variable is of type STATE and if value is a possible value, an object of type sequences or discrete_sequences is returned, otherwise no object is returned. The returned object is of type discrete_sequences if all the variables are of type STATE, if the possible values for each variable are consecutive from 0 and if the number of possible values for each variable is <= 15.
	
  See Also
	
	AddAbsorbingRun,
	Cluster, 
	Cumulate, 
	Difference, 
	IndexExtract, 
	LengthSelect, 
	Merge, 
	MergeVariable, 
	MovingAverage, 
	RemoveRun, 
	Reverse, 
	SegmentationExtract, 
	SelectIndividual, 
	SelectVariable, 
	Shift, 
	Transcode, 
	ValueSelect,
	VariableScaling.
"""
