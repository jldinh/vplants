# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Difference
	First-order differencing of sequences.
  Usage
	Difference(seq, Variable->1, FirstElement->True)	
  Arguments
	seq (sequences, discrete_sequences, markov_data, semi-markov_data).
	
  Optional Arguments 
	Variable (int): variable index,
	FirstElement (bool): first element of sequences kept or not (default value: False).
	
  Returned Object
	The returned object is of type sequences or discrete_sequences. The returned object is of type discrete_sequences if all the variables are of type STATE, if the possible values for each variable are consecutive from 0 and if the number of possible values for each variable is < 15.	
  Background
	If the first element of sequences are kept (FirstValue->True), Difference is the inverse function of Cumulate.
  See Also
	
	AddAbsorbingRun, 
	Cluster, 
	Cumulate, 
	IndexExtract, 
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
	ValueSelect,
	VariableScaling.
"""
