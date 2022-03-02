# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Shift
	Shifting of values.
  Usage
	Shift(histo, param)
	
	Shift(vec1, param)
	Shift(vecn, variable, param)
	
	Shift(seq1, param)
	Shift(seqn, variable, param)	
  Arguments
	histo (histogram, mixture_data, convolution_data, compound_data),
	
	param (int): shifting parameter,
	
	vec1 (vectors): values,
	vecn (vectors): vectors,
	variable (int): variable index,
	
	seq1 (sequences): univariate sequences,
	seqn (sequences): multivariate sequences.
	
  Returned Object
	If the shifting makes that the lower bound to the possible values is positive, an object of type HISTOGRAM (respectively vectors, sequences or sequences) is returned, otherwise no object is returned. In the case of a first argument of type sequences, the returned object is of type discrete_sequences if all the variables are of type STATE, if the possible values for each variable are consecutive from 0 and if the number of possible values for each variable is <= 15.
	
  See Also
	 
	Cluster, 
	Merge, 
	Transcode, 
	MergeVariable, 
	SelectIndividual, 
	SelectVariable, 
	AddAbsorbingRun,
	Cumulate, 
	Difference, 
	Lengthselect, 
	MovingAverage, 
	IndexExtract, 
	RecurrenceTimeSequences, 
	RemoveRun, 
	Reverse, 
	SegmentationExtract, 
	ValueSelect,
	VariableScaling.
"""
