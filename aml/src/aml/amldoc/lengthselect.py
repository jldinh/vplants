# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
LengthSelect
	Selection of sequences according to a length criterion.
  Usage
	LengthSelect(seq, length, Mode->"Reject")
	LengthSelect(seq, min_length, max_length, Mode->"Reject")	
  Arguments
	seq (sequences, discrete_sequences, markov_data, semi-markov_data),
	length (int): length,
	min_length (int): minimum length,
	max_length (int): maximum length.
	
  Optional Arguments 
	Mode (string): conservation or rejection of the selected sequences: "Keep" (the default) or "Reject".
	
  Returned Object
	If length > 0 or if 0 < min_length < max_length and if the range of lengths defined either by length or by min_length and max_length enables to select sequences, an object of type sequences or discrete_sequences is returned, otherwise no object is returned. The returned object is of type discrete_sequences if all the variables are of type STATE, if the possible values for each variable are consecutive from 0 and if the number of possible values for each variable is < 15.
	
  See Also
	
	AddAbsorbingRun,
	Cluster, 
	Cumulate, 
	Difference, 
	IndexExtract, 
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
