# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
SegmentationExtract 
	Extraction by segmentation of sub-sequences.
  Usage
	SegmentationExtract(seqn, variable, value, Mode->"Reject")
	SegmentationExtract(seqn, variable, values, Mode->"Reject")	
  Arguments
	seqn (sequences, discrete_sequences, markov_data, semi-markov_data): multivariate sequences,
	variable (int): variable index,
	value (int): value,
	values (ARRAY(int)): values.
	
  Optional Arguments 
	Mode (string): conservation or rejection of the selected sub-sequences: "Keep" (the default) or "Reject".
	
  Returned Object
	If all the variables are of type STATE, if variable is a valid index of variable and if either value or values@1, ..., values@n are possible values, an object of type sequences or discrete_sequences is returned, otherwise no object is returned. The returned object is of type discrete_sequences if all the variables are of type STATE, if the possible values for each variable are consecutive from 0 and if the number of possible values for each variable is <= 15.
  Description
	Sub-sequences corresponding to run of value or values@1, ..., values@n are extracted (or to all the possible values except value or values@1, ..., values@n) are extracted.
	
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
	RemoveRun, 
	Reverse, 
	SelectIndividual, 
	SelectVariable, 
	Shift, 
	Transcode, 
	ValueSelect,
	VariableScaling.
"""
