# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Transcode 
	Transcoding of values.
  Usage
	Transcode(histo, new_values)
	
	Transcode(vec1, new_values)
	Transcode(vecn, variable, new_values)
	
	Transcode(seq1, new_values)
	Transcode(seqn, variable, new_values)
	Transcode(discrete_seq1, new_values, AddVariable->True)
	Transcode(discrete_seqn, variable, new_values,
	AddVariable->True)
	
  Arguments
	histo (histogram, mixture_data, convolution_data, compound_data),
	new_values (array(int)): new values replacing the old ones min, min + 1, ..., max.
	
	vec1 (vectors): values,
	vecn (vectors): vectors,
	variable (int): variable index,
	
	seq1 (sequences): univariate sequences,
	seqn (sequences): multivariate sequences,
	discrete_seq1 (discrete_sequences, markov_data, semi-markov_data): discrete univariate sequences,
	discrete_seqn (discrete_sequences, markov_data, semi-markov_data): discrete multivariate sequences.
	
  Optional Arguments 
	AddVariable (bool): addition (instead of simple replacement) of the variable to which the transcoding is applied (default value: False). This optional argument can only be used if the first argument is of type discrete_sequences, markov_data, semi-markov_data.
	
  Returned Object
	If the new values are in same number as the old values and are consecutive from 0, an object of type HISTOGRAM is returned (respectively vectors, sequences or discrete_sequences), otherwise no object is returned. In the case of a first argument of type sequences, the returned object is of type discrete_sequences if all the variables are of type STATE, if the possible values for each variable are consecutive from 0 and if the number of possible values for each variable is <= 15.	
  Background
	The function Cluster with the mode "Limit" can be seen as a dedicated interface of the more general function Transcode.
	
  See Also
	Cluster, 
	Merge, 
	Shift, 
	ValueSelect, 
	MergeVariable, 
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
