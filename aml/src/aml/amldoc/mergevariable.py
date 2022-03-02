# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
MergeVariable
	Merging of variables.
  Usage
	MergeVariable (vec1, vec2,..., RefSample->2)
	
	MergeVariable (seq1, seq2,..., RefSample->2)
	
  Arguments
	vec1, vec2, ... (vectors),
	
	seq1, seq2, ... (sequences, discrete_sequences, markov_data, semi-markov_data).
	
  Optional Arguments 
	RefSample (int): reference sample to define individual identifiers (the default: no reference sample).
  Returned Object
	
	 If the arguments are of type vectors and if the number of vectors is the same for each sample, an object of type vectors is returned, otherwise no object is returned.

	 If the arguments are of type sequences, discrete_sequences, markov_data, semi-markov_data, if all the variables are of type STATE, and if the number and the lengths of sequences are the same for each sample, an object of type sequences or discrete_sequences is returned, otherwise no object is returned. The returned object is of type discrete_sequences if all the variables are of type STATE, if the possible values for each variable are consecutive from 0 and if the number of possible values for each variable is <15.
	
  See Also
	Merge,
	Cluster, 
	Shift, 
	Transcode,
	ValueSelect, 
	SelectIndividual, 
	SelectVariable, 
	AddAbsorbingRun,
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
