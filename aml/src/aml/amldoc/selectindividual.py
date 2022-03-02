# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
SelectIndividual
	Selection of vectors, sequences, tops or patterns (in a dissimilarity matrix).
  Usage
	SelectIndividual(vec, identifiers, Mode="Reject")
	SelectIndividual(seq, identifiers, Modei="Reject")
	SelectIndividual(top, identifiers, Modei="Reject")
	SelectIndividual(dist_matrix, identifiers, Modei="Reject")
	
  Arguments
	vec (vectors),
	
	seq (sequences, discrete_sequences, markov_data, semi-markov_data),
	
	top (tops),
	
	dist_matrix (distance_matrix),
	
	identifiers (array(int)): identifiers.
	
  Optional Arguments 
	Mode (string): conservation or rejection of the selected individuals: "Keep" (the default) or "Reject".
	
  Returned Object
	If identifiers@1, ..., identifiers@n are valid identifiers of vectors (respectively sequences, tops or patterns compared in a dissimilarity matrix), an object of type vectors (respectively sequences or discrete_sequences, tops or distance_matrix) is returned, otherwise no object is returned. In the case of a first argument of type sequences, discrete_sequences, markov_data, semi-markov_data, the returned object is of type discrete_sequences if all the variables are of type STATE, if the possible values for each variable are consecutive from 0 and if the number of possible values for each variable is <= 15.
	
  See Also
	Cluster, 
	Merge, 
	Shift, 
	Transcode, 
	ValueSelect,
	MergeVariable, 
	SelectVariable, 
	AddAbsorbingRun,
	Cumulate, 
	Difference, 
	IndexExtract, 
	LengthSelect, 
	MovingAverage, 
	RecurrenceTimeSequences, 
	RemoveSeries, 
	Reverse, 
	SegmentationExtract, 
	VariableScaling, 
	RemoveApicalInternodes, 
	Symmetrize.
"""
