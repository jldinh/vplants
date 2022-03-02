# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Cumulate
	Sum of successive values along sequences.
  Usage
	Cumulate(seq, Variable->1)	
  Arguments
	seq (sequences, discrete_sequences, markov_data, semi-markov_data).
	
  Optional Arguments 
	Variable (int): variable index.
	
  Returned Object
	The returned object is of type sequences or discrete_sequences. The returned object is of type discrete_sequences if all the variables are of type STATE, if the possible values for each variable are consecutive from 0 and if the number of possible values for each variable is < 15.
  Background
	Cumulate is the inverse function of Difference with the optional argument FirstValue set at True.
	
  See Also
	
	AddAbsorbingRun, 
	Cluster, 
	Difference, 
	IndexSelect, 
	LengthSelect, 
	Merge, 
	MergeVariable, 
	MovingAverage, 
	RecurrenceTimeSequences, 
	RemoveSeries, 
	Reverse, 
	SegmentationExtract, 
	SelectIndividual, 
	SelectVariable, 
	Shift, 
	Transcode, 
	ValueSelect
	VariableScaling.
"""
