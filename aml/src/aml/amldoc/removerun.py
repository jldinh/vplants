# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
RemoveRun
	Removal of the first or last run of a given value (for a given variable) in a sequence.
  Usage
	RemoveRun(seq1, value, position, MaxLength->4)
	RemoveRun(seqn, variable, value, position, MaxLength->4)	
  Arguments
	seq1 (sequences, discrete_sequences, markov_data, semi-markov_data): univariate sequences,
	seqn (sequences, discrete_sequences, markov_data, semi-markov_data): multivariate sequences,
	variable (int): variable index,
	value (int): value,
	position (string): position of the removed run: "Begin" or "End".
	
  Optional Arguments 
	MaxLength (int): maximum length of the removed run (default behaviour: the entire run is removed).
	
  Returned Object
	If variable is a valid index of variable, if value is a possible value and if MaxLength > 0, an object of type sequences or discrete_sequences is returned, otherwise no object is returned. The returned object is of type discrete_sequences if all the variables are of type STATE, if the possible values for each variable are consecutive from 0 and if the number of possible values for each variable is <= 15.
	
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
	RecurrenceTimeSequences, 
	Reverse, 
	SegmentationExtract, 
	SelectIndividual, 
	SelectVariable, 
	Shift, 
	Transcode, 
	ValueSelect,
	VariableScaling.
"""
