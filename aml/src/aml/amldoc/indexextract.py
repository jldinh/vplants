# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
IndexExtract
	Extraction of sub-sequences corresponding to a range of index parameters.
  Usage
	IndexExtract(seq, min_index, MaxIndex->40)	
  Arguments
	seq (sequences, discrete_sequences, markov_data, semi-markov_data),
	min_index (int): minimum index parameter.
	
  Optional Arguments 
	MaxIndex (int): maximum index parameter (default behaviour: the end of sequences is kept).
	
  Returned Object
	If 0 < min_index < (maximum index parameter if the optional argument MaxIndex is set) < (maximum length of sequences), the returned object is of type sequences or discrete_sequences, otherwise no object is returned. The returned object is of type discrete_sequences if all the variables are of type STATE, if the possible values for each variable are consecutive from 0 and if the number of possible values for each variable is < 15.
	
  See Also
	
	AddAbsorbingRun,
	Cluster, 
	Cumulate, 
	Difference, 
	LengthSelect, 
	Merge, 
	MergeVariable, 
	MovingAverage, 
	RecurrenceTimeSequences, 
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
